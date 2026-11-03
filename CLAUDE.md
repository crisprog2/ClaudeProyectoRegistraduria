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

Figma: https://www.figma.com/design/olhIBoGbGoNDJ9LBxbxiqz/Proyecto-Registraduria — no es accesible desde Claude; el usuario comparte capturas cuando hace falta.

Dos pantallas:
1. **Consulta** (`/consulta`): encabezado, `CedulaForm`, `PromoPanel` ("Tu voz cuenta"), `PasosConsulta`.
2. **Resultado** (`/consulta/resultado`): `CiudadanoResumen`, `LugarVotacionCard`, `MapaPuesto` y, **solo si es jurado**, `JuradoAlert`, `AsignacionJuradoCard` y `ResponsabilidadesNota`.

Layout común: `TopBar`, `SiteHeader`, `MainNav`, `FlagStripe`, `DemoBanner`, `Breadcrumb`, `Stepper`, `SiteFooter`.

## Decisiones tomadas

- Un ciudadano que **no es jurado** es solo votante: el resultado muestra únicamente el lugar de votación. **No existe** un mensaje "no eres jurado". Las pruebas deben verificar la **ausencia** de las secciones de jurado.
- "Cómo consultar" y "Ayuda" en `MainNav` son **enlaces solo visuales**; no tienen página.
- La cédula viaja por **estado de navegación**, nunca en la URL.
- La cédula se ingresa solo con dígitos y se **muestra formateada** con puntos (`1.098.765.432`).
- Los estados de error (`FormError`, `ConsultaSinResultado`) no están diseñados en Figma; se diseñarán siguiendo el estilo existente.
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
- `edad` no se guarda: es una propiedad calculada desde `fecha_nacimiento`. En pruebas usar `calcular_edad(fecha_referencia)` para que el resultado no dependa del día en que se ejecuta.
- `PROTECT` en todas las FK de referencia; solo `DesignacionJurado.persona` usa `CASCADE`.
- `segundo_nombre` y `segundo_apellido` son opcionales; `genero` admite `F`, `M` u `O`.
- La validación de formato de la cédula (solo dígitos, longitud) va en `validators.py`, no en el modelo.

Convenciones del modelo:
- Campos en snake_case; las FK se nombran como el objeto (`departamento`, `puesto`, `mesa`) y usan `db_column='cod_*'`.
- El nombre visible de cada entidad es `nombre` (no repetir el nombre del modelo).
- Docstring por modelo con la lista de campos. Indentación de 4 espacios (PEP 8).

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

## Estado

- ✅ Estructura base del monorepo.
- ✅ Modelo de datos definido y revisado (validado con system checks y pruebas en SQLite en memoria).
- ✅ Entorno virtual `.venv/` con dependencias fijadas y navegadores de Playwright.
- ⏳ Siguiente: configurar `settings` de Django, crear la base de datos y el usuario en MySQL (el usuario ejecuta los comandos con su contraseña de root) y generar las migraciones.
- ⏳ El resto de archivos de código siguen con solo un comentario de propósito. Las instrucciones de ejecución del README están pendientes.
