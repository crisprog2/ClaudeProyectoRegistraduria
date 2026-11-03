# CLAUDE.md

Contexto y convenciones para futuras sesiones de trabajo en este repositorio.

## Contexto

Proyecto de **portafolio de un Quality Engineer**. El objetivo principal es mostrar buenas prácticas de QA y automatización de pruebas sobre una app web full stack; la app en sí es el sistema bajo prueba.

**ConsultaVoto** es una app **ficticia** de consulta electoral:
- El usuario ingresa su número de cédula.
- Se muestra su lugar de votación: puesto, dirección, ciudad, departamento y mesa.
- Si fue designado jurado, se muestra además su asignación: rol (p. ej. "Jurado titular"), puesto, dirección y mesa de servicio, que **pueden ser distintos** a donde vota.
- Casos de error: campo vacío, formato inválido y cédula no encontrada.

## Reglas de marca y datos (no negociables)

- Marca ficticia: **ConsultaVoto** — subtítulo "Proyecto de portafolio QA". **No** usar "Registraduría Nacional del Estado Civil" ni ningún nombre o logo de entidades reales.
- El sitio no debe parecer oficial: siempre visibles el `DemoBanner`, el badge "DATOS FICTICIOS" y los avisos de prototipo.
- Solo datos inventados. Nunca cédulas, nombres o direcciones reales.

## Stack

- **Backend**: Python 3.11 + Django 5.2 LTS + Django REST Framework + MySQL 8.0. No subir a Django 6: exige Python 3.12+.
- **Entorno**: un solo entorno virtual en la raíz (`.venv/`) para backend y pruebas. Versiones fijadas con `==` en `backend/requirements.txt` y `tests/requirements.txt`. Navegadores de Playwright (Chromium, Firefox, WebKit) instalados fuera del repo.
- **Base de datos**: servidor MySQL 8.0 **local** del usuario (servicio de Windows, puerto 3306). No se usa Docker. En CI se usa el contenedor `mysql:8.0` como servicio de GitHub Actions para mantener la misma versión mayor.
- **Frontend**: React + Vite + react-router-dom.
- **Pruebas** (todas en Python):
  - `backend/tests/` — white-box, pytest + pytest-django.
  - `tests/api/` — black-box de la API, pytest + requests.
  - `tests/bdd/` — pytest-bdd, Gherkin **en español** (`# language: es`).
  - `tests/e2e/` — Playwright para Python (pytest-playwright).
- **CI**: GitHub Actions en `.github/workflows/ci.yml`.

## Diseño (Figma)

Figma: https://www.figma.com/design/olhIBoGbGoNDJ9LBxbxiqz/Proyecto-Registraduria (fileKey `olhIBoGbGoNDJ9LBxbxiqz`). Accesible con el servidor MCP de Figma (alcance user): **lectura y edición funcionan**. Antes de editar con `use_figma` cargar las guías `figma-use` y `figma-generate-design`. El archivo no tiene variables, estilos ni componentes: se reutilizan los valores de las pantallas existentes (Inter; textos `#142c43` / `#53677b`; bordes `#dce4ed` / `#9aabbe`; azul `#1658c1`; rojo `#c9454c`).

Frames (página `0:1`):
- `6:2319` Consulta electoral · Inicio
- `17:2` Consulta electoral · Error campo vacío
- `17:145` Consulta electoral · Error formato inválido
- `17:288` Consulta electoral · Cédula no encontrada
- `6:2442` Resultado · Votante sin designación
- `6:2609` Resultado · Votante y jurado

Pantallas y componentes:
1. **Consulta** (`/consulta`): encabezado, `CedulaForm`, `PromoPanel` ("Tu voz cuenta"), `PasosConsulta`. Estados de error **debajo del campo, en lugar del texto de ayuda**:
   - Campo vacío → `FormError`: borde rojo + "Ingresa tu número de cédula para consultar."
   - Formato inválido → `FormError`: borde rojo + "El número no es válido. Escribe solo números, sin puntos, espacios ni comas."
   - No encontrada → `ConsultaSinResultado`: panel rojo claro, borde normal en el campo, "No encontramos información para esta cédula" + "Verifica el número e inténtalo de nuevo. Solo existen cédulas de ejemplo."
2. **Resultado** (`/consulta/resultado`): `CiudadanoResumen`, `LugarVotacionCard`, `MapaPuesto` y además:
   - **Solo votante:** `VotanteAlert` (badge VOTANTE) y `ConsejoVotacion` ("Antes de ir a votar"). `CiudadanoResumen` muestra la edad.
   - **Jurado:** `JuradoAlert` (badge JURADO), `AsignacionJuradoCard` y `ResponsabilidadesNota`.

Layout común: `TopBar`, `SiteHeader`, `MainNav`, `FlagStripe`, `DemoBanner`, `Breadcrumb`, `Stepper`, `SiteFooter`.

## Decisiones tomadas

- Un ciudadano que **no es jurado** es solo votante: el resultado muestra el aviso `VotanteAlert` con el texto **neutro** "Eres votante y no tienes designación como jurado" (no depende del género), el lugar de votación y el consejo "Antes de ir a votar". Las pruebas deben verificar la **presencia** de ese aviso y la **ausencia** de las secciones de jurado.
- La pantalla del votante muestra la **edad** ("Edad · 32 años"); la del jurado no (así está en el Figma). La API devuelve la edad en ambos casos y el frontend decide si la muestra.
- "Cómo consultar" y "Ayuda" en `MainNav` son **enlaces solo visuales**; no tienen página.
- La cédula viaja por **estado de navegación**, nunca en la URL.
- La cédula se ingresa solo con dígitos y se **muestra formateada** con puntos (`1.098.765.432`).
- Los estados de error (`FormError`, `ConsultaSinResultado`) están diseñados en Figma (frames `17:2`, `17:145`, `17:288`). El mensaje de formato inválido no menciona la longitud hasta que se defina la regla de la cédula.
- **`backend/apps/consultas/models.py` es del usuario.** Lo escribió el usuario y se ajustó con revisión de Claude. Cualquier cambio estructural al modelo se propone y se aplica solo con su aprobación.

## Modelo de datos

`backend/apps/consultas/models.py` (diagrama ER en el README):

- `Departamento` (PK `cod_departamento`, 2 car.) → `Ciudad` (PK `cod_ciudad`, 5 car.) → `PuestoVotacion` (PK `cod_puesto`, ≤10 car.) → `Mesa` (PK `cod_mesa` autoincremental, `numero` único por puesto).
- `Persona` (PK `cedula` CharField ≤10, solo dígitos) → `mesa` donde vota.
- `DesignacionJurado`: OneToOne `persona` (`related_name='designacion_jurado'`), `mesa_servicio` y `rol` (`TITULAR` / `REMANENTE`).
- Relaciones inversas: `departamento.ciudades`, `ciudad.puestos`, `puesto.mesas`, `mesa.votantes`, `mesa.jurados`.

Reglas:
- Es jurado ⇔ existe `DesignacionJurado` (`hasattr(persona, 'designacion_jurado')`). No hay campo booleano.
- El puesto, la dirección, la ciudad y el departamento de servicio se obtienen de `mesa_servicio.puesto`; no se duplican.
- `nombre_completo` es una propiedad del modelo (omite segundo nombre/apellido vacíos); el admin y la API la reutilizan.
- `edad` no se guarda: es una propiedad calculada desde `fecha_nacimiento`. En pruebas usar `calcular_edad(fecha_referencia)` para que el resultado no dependa del día en que se ejecuta.
- `PROTECT` en todas las FK de referencia; solo `DesignacionJurado.persona` usa `CASCADE`.
- `segundo_nombre` y `segundo_apellido` son opcionales; `genero` admite `F`, `M` u `O`.
- La validación de formato de la cédula (solo dígitos, longitud) va en `validators.py`, no en el modelo.

Convenciones del modelo:
- Campos en snake_case; las FK se nombran como el objeto (`departamento`, `puesto`, `mesa`) y usan `db_column='cod_*'`.
- El nombre visible de cada entidad es `nombre` (no repetir el nombre del modelo).
- Docstring por modelo con la lista de campos. Indentación de 4 espacios (PEP 8).
- `__str__` legible, sin IDs internos: `Mesa 018 · Colegio Cívico La Esperanza`, `Jurado titular · Carlos Martínez · Mesa 018 · Colegio Cívico La Esperanza`. Los de `Mesa` y `DesignacionJurado` leen modelos relacionados: en listados usar `select_related`. Cambiar un `__str__` no genera migración.

## Admin de Django

`backend/apps/consultas/admin.py` registra los 6 modelos para revisar los datos de demostración:
- Listados con `list_select_related` (sin consultas por fila) y `autocomplete_fields` para las relaciones (el admin relacionado debe tener `search_fields`).
- `PersonaAdmin`: columnas de edad calculada, puesto y "es jurado"; filtro propio `EsJuradoFilter` (sí/no); la designación se edita en la misma ficha (`DesignacionJuradoInline`, máximo 1).
- `DesignacionJuradoAdmin`: columna "vota en la misma mesa".

## API REST de consulta

`POST /api/consulta/` con `{"cedula": "..."}` (la cédula nunca va en la URL). Capas:
- `validators.validar_cedula()`: quita espacios externos; exige texto de **6 a 10 dígitos ASCII sin 0 inicial**. Lanza `django.core.exceptions.ValidationError` con código `CEDULA_REQUERIDA` o `CEDULA_FORMATO_INVALIDO` (no depende de DRF).
- `services.consultar_por_cedula()`: una sola consulta SQL (`select_related`, incluida la designación); lanza `CedulaNoEncontrada`.
- `serializers.ResultadoConsultaSerializer`: `ciudadano` (cedula, nombre_completo, edad), `lugar_votacion` (mesa, puesto, direccion, ciudad, departamento) y `jurado` (rol, rol_display, ubicación de la mesa de servicio, misma_mesa) o `null`. La edad usa `timezone.localdate()`. Nunca expone género, fecha de nacimiento ni IDs internos.
- `views.ConsultaView`: solo POST, solo JSON, sin autenticación (por eso sin CSRF), límite `ConsultaRateThrottle`.
- `exceptions.manejador_de_errores` (EXCEPTION_HANDLER): todas las respuestas de error son `{"codigo", "mensaje"}`.

| HTTP | `codigo` |
|---|---|
| 400 | `CEDULA_REQUERIDA`, `CEDULA_FORMATO_INVALIDO`, `SOLICITUD_INVALIDA` (JSON mal formado o que no es objeto) |
| 404 | `CEDULA_NO_ENCONTRADA` |
| 405 | `METODO_NO_PERMITIDO` |
| 415 | `SOLICITUD_INVALIDA` (no es JSON) |
| 429 | `DEMASIADAS_CONSULTAS` (más de 30/min por IP; incluye `Retry-After`) |

Los mensajes son los textos del Figma. Seguridad: `NUM_PROXIES = 0` hace que el límite use `REMOTE_ADDR`; con el valor por defecto de DRF se podría evadir falsificando `X-Forwarded-For` (hay una prueba que lo verifica).

Pruebas white-box (`backend/tests/`, 77): `test_models.py` (`nombre_completo` y días límite de `calcular_edad`), `test_validators.py`, `test_services.py` (incluye "exactamente 1 consulta SQL") y `test_api_consulta.py` (JSON exacto de los casos del Figma, todos los errores, límite de consultas y X-Forwarded-For). `conftest.py`: `datos_demo`, `fecha_fija` (edad estable), `limpiar_cache` (autouse: el contador del límite vive en la caché) y `consultar`. Se ejecutan con `cd backend; pytest`.

## Convenciones

- **Idioma**: dominio, nombres de archivos, componentes, tests y features en español (`ConsultaPage`, `test_validaciones_cedula.py`). Términos técnicos estándar en inglés (`conftest`, `services`, `hooks`).
- **Backend**: lógica en `services.py`, reglas de formato en `validators.py`; las vistas se mantienen delgadas.
- **Frontend**: `pages/` = una por pantalla; `components/` agrupado por `layout/`, `common/`, `consulta/` y `resultado/`. Llamadas HTTP solo desde `services/api.js`. Colores y tipografía en `styles/tokens.css`.
- **Pruebas**:
  - Page Object Model en `tests/support/pages/`, compartido por E2E y BDD. Los tests no usan selectores directamente.
  - Un `conftest.py` por nivel (`tests/`, `tests/api/`, `tests/bdd/`, `tests/e2e/`, `backend/tests/`).
  - Datos de prueba en `tests/data/*.json`; nada de datos quemados en los tests.
  - BDD: `features/` separado de `step_defs/`; los steps reutilizables van en `common_steps.py`.
  - Markers declarados en `pytest.ini` (`api`, `bdd`, `e2e`, `smoke`, `regression`); `--strict-markers` activo.
  - Escenarios mínimos a cubrir: solo votante, jurado en la misma mesa, jurado en otra mesa o puesto, campo vacío, formato inválido y cédula no encontrada.
- **Configuración**: todo por variables de entorno (ver `.env.example`); nunca subir `.env`.
- **Documentación del código**: docstring en cada módulo, clase y función pública, en español. Los `__str__` llevan un ejemplo del texto que producen. Las clases `Meta` no necesitan docstring. En pruebas, el nombre `test_*` describe el caso; el docstring solo se agrega cuando la intención no es obvia.
- **Pruebas que importan**: cuando una prueba protege una regla de seguridad o de negocio, comprobar al menos una vez que falla si se reintroduce el defecto (prueba de mutación), no solo que pasa.
- **Al terminar una tarea**: actualizar la sección "Estado" de este archivo y, si cambia algo visible para quien usa el repo, el README (tabla "Estado del proyecto" y "Ejecución").

## Estado

- ✅ Estructura base del monorepo.
- ✅ Modelo de datos definido y revisado (validado con system checks y pruebas en SQLite en memoria).
- ✅ Entorno virtual `.venv/` con dependencias fijadas y navegadores de Playwright.
- ✅ Settings de Django (`base` / `local` / `test`) leyendo del `.env` de la raíz. `manage.py` usa `local` por defecto y `backend/pytest.ini` usa `test`.
- ✅ Base local `registraduria` (utf8mb4_0900_ai_ci, modo estricto) con usuario `consultavoto_app`, que solo tiene permisos sobre `registraduria` y `test_registraduria`. Migración `0001_initial` aplicada.
- ✅ Fixture `backend/apps/consultas/fixtures/datos_demo.json` cargado en `registraduria` (`python manage.py loaddata datos_demo`).
- ✅ Admin de Django configurado para los 6 modelos; `__str__` legibles en `Mesa` y `DesignacionJurado`.
- ✅ Código del backend documentado con docstrings; README con instrucciones de ejecución del backend.
- ✅ Superusuario local creado por el usuario (no compartir ni registrar su contraseña).
- ✅ Figma actualizado: marca ConsultaVoto en las 3 pantallas, aviso neutro del votante y 3 pantallas de estados de error. Fixture alineado con el Figma (cédula `1023456789`).
- ✅ API REST de consulta (`POST /api/consulta/`) con manejador central de errores y límite de consultas por IP.
- ✅ Pruebas white-box del backend: 77 pasan contra MySQL; mutación de `NUM_PROXIES` detectada.
- ⏳ Siguiente: datos de `tests/data/` y pruebas black-box de API (`tests/api/`), o empezar el frontend.

## Datos de demostración (`datos_demo.json`)

- **Geografía real (pública):** los 33 departamentos con código DIVIPOLA del DANE, sus capitales y algunos municipios extra (39 ciudades).
- **Todo lo demás es ficticio:** puestos (código = municipio 5 + zona 2 + puesto 2), mesas, personas y designaciones. Las cédulas siguen el formato colombiano (antiguas de 7-8 dígitos, actuales de 10); cualquier coincidencia con una cédula real es accidental.

| Cédula | Escenario |
|---|---|
| `1098765432` | Jurado titular en la **misma mesa** donde vota (caso del Figma: Carlos Andrés Martínez, Mesa 018, Colegio Cívico La Esperanza, Medellín). Sin segundo apellido. |
| `1143987654` | Jurado titular en la misma mesa. Nacida un 29 de febrero. |
| `1017234568` | Jurado remanente en **otra mesa del mismo puesto**. Sin segundo nombre; apellido con ñ. |
| `52748193` | Jurado remanente en otra mesa del mismo puesto. Cédula antigua de 8 dígitos. |
| `1036845120` | Jurado titular en **otro puesto** de la misma ciudad. |
| `1023456789` | Solo votante (caso del Figma "Votante sin designación": Laura Camila Gómez, 32 años, Mesa 012, Colegio Cívico La Esperanza, Medellín). Sin segundo apellido. |
| `1144056789` | Solo votante. |
| `79563214` | Solo votante. Cédula antigua de 8 dígitos. |
| `1095827364` | Solo votante. 18 años, género O, sin segundo nombre. |
| `4567891` | Solo votante. Cédula antigua de 7 dígitos, mayor edad. |
| `1000000000` | **No registrada** (no existe en el fixture). |
