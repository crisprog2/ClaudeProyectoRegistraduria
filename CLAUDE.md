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

- **Backend**: Python + Django + Django REST Framework + MySQL 8.0.
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
- **`backend/apps/consultas/models.py` lo escribe el usuario.** Claude solo revisa y sugiere ajustes; no lo redacta por iniciativa propia.

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

Fase actual: **estructura base creada, sin implementación**. Los archivos de código contienen solo un comentario de propósito. Las instrucciones de ejecución del README están pendientes.
