# ADR 0002 · Token de acceso en memoria y token de refresco en una cookie HttpOnly

- **Estado:** Aceptada
- **Fecha:** 2026-11-18
- **Aprobada por:** el dueño del producto, que pidió dejar documentado por qué esta opción es mejor
- **Fase:** 1 · Autenticación y roles

## Contexto

El administrador y el analista inician sesión con JWT (*JSON Web Token*, con la librería `djangorestframework-simplejwt`). Al iniciar sesión, el servidor entrega dos tokens:

| Token | Para qué | Duración |
|---|---|---|
| **De acceso** | Acompaña cada petición protegida (`Authorization: Bearer <token>`) | 15 minutos |
| **De refresco** | Pide un token de acceso nuevo sin volver a escribir la contraseña | 8 horas como máximo desde el inicio de sesión |

El servidor **no guarda** el token de acceso. Va firmado con la clave secreta del servidor, y en cada petición se comprueban tres cosas:

1. que la firma sea válida (si alguien cambia una letra, deja de serlo);
2. que no haya vencido;
3. que el usuario siga activo y con su rol en la base de datos.

El token de refresco, en cambio, sí deja rastro en la base (tablas `token_blacklist_*`), para poder **revocarlo**.

La pregunta es **dónde guarda el navegador esos tokens**. Quien tenga el token de refresco puede actuar como el usuario durante horas.

## La amenaza principal: XSS

Un ataque de *cross-site scripting* (XSS) ocurre cuando alguien logra ejecutar su propio JavaScript dentro de la página. Puede ser por un campo mal escapado o por una librería de terceros comprometida. Ese código puede leer todo lo que JavaScript puede leer.

## Opciones consideradas

| | **A. Los dos tokens en `localStorage`** | **B. El de acceso en memoria y el de refresco en una cookie `HttpOnly`** |
|---|---|---|
| Dónde queda el token de acceso | En el almacenamiento del navegador | En una variable de la página; desaparece al cerrarla |
| Dónde queda el token de refresco | En el almacenamiento del navegador | En una cookie que JavaScript **no puede leer** |
| Si hay un XSS | El atacante **copia los dos tokens** y los usa desde su propio equipo durante horas, aunque la víctima cierre la página | El atacante no puede llevarse el token de refresco. Solo puede actuar mientras la página siga abierta, y lo que robe del token de acceso vence en 15 minutos |
| Al recargar la página | La sesión sigue | La sesión sigue: la página pide un token de acceso nuevo y el navegador envía la cookie solo |
| Peticiones falsificadas desde otro sitio (CSRF) | No aplica: el navegador no envía `localStorage` solo | Hay que protegerse, porque el navegador sí envía cookies solo. Se resuelve con `SameSite=Strict` y una cabecera propia (ver abajo) |
| Esfuerzo | Menor | Mayor |
| Opinión de un revisor de seguridad | Es una debilidad conocida y suele señalarse | Es la recomendación habitual para aplicaciones de una sola página |

## Decisión

**Opción B.**

### Por qué es mejor

1. **Limita el daño de un XSS, que es la amenaza más probable.** Con `localStorage`, un solo fallo de escape en cualquier pantalla entrega la sesión completa al atacante, para usarla donde quiera. Con la cookie `HttpOnly`, el navegador se niega a mostrarle el token de refresco a cualquier JavaScript, incluido el del atacante.
2. **La ventana de daño es corta.** El único token que JavaScript ve es el de acceso, que dura 15 minutos y vive en la memoria de la página.
3. **Cerrar sesión cierra la sesión de verdad.** El token de refresco queda revocado en el servidor y la cookie se borra. Con `localStorage`, una copia robada seguiría sirviendo hasta vencer.
4. **El riesgo nuevo (CSRF) se cubre con dos capas:**
   - `SameSite=Strict`: el navegador no envía la cookie si la petición viene de otro sitio.
   - La cabecera propia `X-Requested-With: ConsultaVoto`, obligatoria en `refrescar` y `salir`. Una página ajena no puede agregar cabeceras propias sin una verificación de CORS, y CORS solo admite el origen del frontend.

   Se prefirió a la cabecera estándar de CSRF de Django porque no exige pedir ni guardar un token adicional en el frontend, y en una aplicación de una sola página protege igual.

### Detalles

| Elemento | Valor | Por qué |
|---|---|---|
| Nombre de la cookie | `consultavoto_refresco` | |
| `HttpOnly` | Sí | JavaScript no puede leerla |
| `SameSite` | `Strict` | No viaja en peticiones que vienen de otro sitio |
| `Path` | `/api/auth/` | Solo viaja a `refrescar` y `salir`, no en cada petición |
| `Max-Age` | Lo que le queda al token, como máximo 8 horas | La cookie no sobrevive a su token |
| `Secure` | Variable `JWT_COOKIE_SECURE` | Solo HTTPS. Apagado en local y en el CI, que usan `http://`, donde la cookie no viajaría. **Debe activarse en cualquier despliegue real** |
| Rotación | En cada `refrescar` se revoca el token anterior y se entrega uno nuevo | Un token de refresco robado y ya usado deja de servir |
| Vencimiento al rotar | Se **conserva** el del token original | La rotación de simplejwt renueva el vencimiento: con cada renovación la sesión se alargaría sin fin. Aquí dura como máximo 8 horas desde el inicio de sesión |
| Usuario borrado al refrescar | 401 `SESION_EXPIRADA` | El serializador de simplejwt lanzaría una excepción no controlada (un 500); por eso la rotación está en `apps/cuentas/services.py` |
| Errores de inicio de sesión | El mismo 401 para un usuario inexistente, una contraseña incorrecta, un usuario desactivado o sin rol y el superusuario | Nadie puede averiguar qué usuarios existen |
| Límite de intentos | 5 por minuto por IP (`INGRESO_LIMITE_POR_MINUTO`) | Frena los ataques de fuerza bruta. Identifica por `REMOTE_ADDR`, así que falsificar `X-Forwarded-For` no lo evade |

## Consecuencias

- **A favor:** menor impacto de un XSS, cierre de sesión real y sesión con un límite de duración.
- **En contra:**
  - más piezas (la cookie, la cabecera y la rotación propia) y por eso más pruebas;
  - el frontend debe renovar el token de acceso antes de que venza (fase 5).
- **Límites conocidos (son del diseño de JWT, no de esta opción):**
  - Al cerrar sesión, el token de acceso ya entregado sigue siendo válido hasta que vence, 15 minutos como máximo, porque el servidor no lo guarda. El frontend lo borra de su memoria al salir.
  - Ninguna forma de guardar tokens anula un XSS: mientras la página esté abierta, el código inyectado puede hacer peticiones como el usuario. La opción B limita el daño; evitar el XSS sigue siendo trabajo de la interfaz (React escapa el contenido por defecto).

## Cómo se verifica

- **`backend/tests/test_autenticacion.py` (white-box):**
  - cada atributo de la cookie, incluido `Secure` al activar la variable;
  - el token de refresco no aparece en el JSON;
  - el mismo error para los 5 casos de inicio de sesión fallido;
  - el límite de intentos y que `X-Forwarded-For` no lo evade;
  - la rotación con revocación;
  - que la rotación no alarga la sesión (el token original vence en 1 hora y el renovado debe conservar esa hora);
  - un usuario borrado no causa un 500;
  - la cabecera propia es obligatoria;
  - tokens de acceso vencidos, con la firma alterada, firmados con otra clave, con `alg: none` y de refresco usados como de acceso.
- **`tests/api/test_autenticacion.py` (black-box, contra el servidor real):** la cookie se revisa en la cabecera `Set-Cookie` real; una cookie rotada o la de una sesión cerrada ya no sirve.
- **`tests/bdd/features/inicio_sesion.feature`:** "Cerrar sesión", con el escenario "su sesión ya no se puede renovar".
- **Mutaciones verificadas** (se reintroduce el defecto y se confirma que alguna prueba falla):
  - la cookie sin `HttpOnly` o con `SameSite=Lax`;
  - el token de refresco en el JSON;
  - mensajes distintos para un usuario inexistente;
  - la rotación sin revocar el token anterior, o renovando su vencimiento;
  - cerrar sesión sin revocar;
  - `refrescar` sin exigir la cabecera;
  - sin límite de intentos;
  - un usuario desactivado que conserva el acceso.

  Las 12 mutaciones del backend y las 5 contra el servidor real se detectaron.
