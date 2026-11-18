# ADR 0001 · Roles Administrador y Analista, y administración en una pantalla propia

- **Estado:** Aceptada
- **Fecha:** 2026-11-18
- **Aprobada por:** el dueño del producto
- **Fase:** 1 · Autenticación y roles (el plan completo está en `CLAUDE.md`, sección "Autenticación y roles")

## Contexto

Hasta ahora ConsultaVoto solo tenía un tipo de usuario: el **ciudadano**, que consulta su lugar de votación sin cuenta. El producto necesita dos usuarios más:

- alguien que **administre los datos**: departamentos, ciudades, puestos y direcciones, mesas, personas y quién es jurado;
- alguien que **consulte un reporte** con gráficas de las consultas por género, ciudad y rango de edad.

Esas funciones no pueden quedar abiertas como la consulta: hace falta saber quién es cada usuario y qué puede hacer.

## Opciones consideradas

**¿Dónde administrar los datos?**

| Opción | A favor | En contra |
|---|---|---|
| **A. El admin de Django** (ya existe en `/admin/`) | No hay que construir nada | Es una herramienta técnica, con el aspecto de Django y sin la marca del producto; usa sesiones de Django, no la API; probarlo muestra poco del producto |
| **B. Una pantalla propia** en el frontend, sobre una API protegida | Es parte real del producto; reutiliza la API REST y su manejo de errores; da muchos casos de prueba (permisos por rol, formularios, accesibilidad) | Hay que construir la API y las pantallas |

**¿Dónde guardar los usuarios y los roles?**

| Opción | A favor | En contra |
|---|---|---|
| **A. Un modelo propio** de usuario en `models.py` | Control total | Cifrar contraseñas, validarlas y manejar permisos a mano es fácil de hacer mal; mezclaría las cuentas de acceso con el dominio electoral |
| **B. Los usuarios y grupos de Django** | Contraseñas cifradas con PBKDF2-SHA256 (un millón de iteraciones y una sal aleatoria por usuario), validadores de contraseña ya configurados, integración con DRF y con simplejwt | Ninguno relevante para este proyecto |

## Decisión

1. **Tres tipos de usuario:**

   | Rol | Qué hace | Cómo entra |
   |---|---|---|
   | Ciudadano | Consulta su lugar de votación | Sin cuenta, como hasta ahora |
   | **Administrador** | Edita todos los datos, gestiona usuarios y ve el reporte | Inicia sesión |
   | **Analista** | Solo ve el reporte | Inicia sesión |

2. **La administración es una pantalla propia** (opción B), en `/administracion`. El admin de Django se conserva solo para el superusuario (ver [ADR 0003](0003-admin-de-django-solo-superusuario.md)).
3. **Los usuarios se guardan en las tablas de Django** (opción B), en la misma base MySQL:
   - `auth_user`: los usuarios. La contraseña nunca se guarda tal cual, sino con el formato `pbkdf2_sha256$1000000$<sal>$<hash>`.
   - `auth_group`: los roles. La migración `apps/cuentas/migrations/0001_grupos.py` crea `Administrador` y `Analista` en cualquier base, sin pasos manuales.
   - `auth_user_groups`: qué usuario tiene qué rol.

   `models.py`, que define el dominio electoral, no cambia.
4. **El rol se lee de la base de datos en cada petición**, nunca del token. Así, desactivar a un usuario o quitarle el rol tiene efecto inmediato.
5. **El superusuario no tiene rol en la aplicación:** solo entra al admin de Django.
6. **Reglas de la gestión de usuarios**, que se implementan en las fases 3 y 6:
   - el administrador puede asignar los roles Analista y Administrador;
   - puede cambiar el rol de un usuario, desactivarlo y reactivarlo (no borrarlo);
   - no puede desactivarse ni quitarse el rol a sí mismo;
   - siempre debe quedar al menos un administrador activo;
   - el superusuario no aparece ni se puede modificar;
   - las contraseñas cumplen los validadores de Django y nunca se muestran;
   - quedan fuera, por ahora, cambiar la propia contraseña y recuperarla por correo.

## Consecuencias

- **A favor:** seguridad de contraseñas probada en la industria, sin código propio de cifrado; el dominio electoral queda separado de las cuentas (app `apps/cuentas`); los permisos se reutilizan en las fases siguientes (`EsAdministrador`, `EsAnalistaOAdministrador`).
- **En contra:** leer el rol en cada petición agrega una consulta a la base por petición protegida. Con el volumen de este proyecto es irrelevante, y es el precio de que quitar un rol tenga efecto inmediato.
- **Para el portafolio:** permite mostrar una matriz de permisos por rol, pruebas de escalada de privilegios y pruebas de efecto inmediato.

## Cómo se verifica

- `backend/tests/test_roles_y_permisos.py`:
  - la migración crea los dos grupos;
  - `rol_de()` con cada rol y sin rol, con un usuario desactivado y con el superusuario;
  - la matriz de permisos por rol;
  - ningún permiso admite al anónimo ni al superusuario.
- `backend/tests/test_autenticacion.py`:
  - quitar el rol o desactivar a un usuario le quita el acceso con un token aún vigente;
  - cambiar el rol se refleja sin volver a iniciar sesión;
  - el token no lleva el rol.
- **Mutación verificada:** si los permisos dejaran de leer el rol de la base, fallarían 7 pruebas; si el superusuario tuviera acceso a la aplicación, fallarían 5.
