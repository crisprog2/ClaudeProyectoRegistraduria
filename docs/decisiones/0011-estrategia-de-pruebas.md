# ADR 0011 · Estrategia de pruebas: cuatro niveles en Python, BDD en español por dos canales y Page Objects accesibles

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 a 2026-11-06 (commits `cd2027b`, `fa247ad`, `19b55ae` y `81753ff`)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md` y el README
- **Aprobada por:** el dueño del producto

## Contexto

El objetivo del proyecto es mostrar buenas prácticas de QA. Había que decidir qué niveles de prueba tener, con qué herramientas y cómo organizarlos para que se pudieran mantener.

## Opciones consideradas

| Tema | Alternativas | Elegida y por qué |
|---|---|---|
| Lenguaje de las pruebas | Python para la API y JavaScript/TypeScript para la interfaz | **Todo en Python:** un solo lenguaje, un solo entorno y fixtures compartidas |
| Pruebas de interfaz | Selenium, Cypress, Playwright | **Playwright para Python:** espera automática, Chromium, Firefox y WebKit, y trazas para depurar |
| BDD | Behave, pytest-bdd | **pytest-bdd:** comparte las fixtures, los markers y los plugins de pytest con el resto |
| Idioma de Gherkin | Inglés o español | **Español** (`# language: es`): el producto y quien lo especifica hablan español |
| Selectores | `data-testid`, CSS, XPath | **Rol y nombre accesible** (`get_by_role`, `label`): las pruebas usan la página como un usuario, incluido uno con lector de pantalla |

## Decisión

- **Cuatro niveles**, cada uno en su carpeta con su `conftest.py`:

  | Nivel | Carpeta | Qué prueba |
  |---|---|---|
  | White-box | `backend/tests/` (pytest-django) | Reglas internas, consultas SQL, errores y configuración |
  | Black-box de la API | `tests/api/` (pytest + requests) | El contrato HTTP contra el servidor real, sin importar nada de Django |
  | BDD | `tests/bdd/` (pytest-bdd) | Escenarios de negocio en Gherkin, sin HTTP ni pantallas |
  | E2E | `tests/e2e/` (Playwright) | La interfaz en tres navegadores, la accesibilidad (axe-core) y las pantallas pequeñas |

- **Los mismos features BDD corren por dos canales:** `step_defs/api/` y `step_defs/interfaz/`. Un escenario de negocio se comprueba en la API y en la pantalla. Cada canal tiene su propio `conftest.py` y su `common_steps.py`, porque los textos de los pasos son iguales y sus implementaciones no deben mezclarse.
- **Page Object Model** compartido por E2E y BDD (`tests/support/pages/`). Las pruebas no usan selectores directamente. `data-testid` solo si no hay alternativa accesible.
- **Datos de prueba fuera del código** (`tests/data/*.json`). Los mensajes del Figma y los ejemplos de cédulas inválidas van literales en los features, porque son la especificación.
- **Markers declarados** (`api`, `bdd`, `e2e`, `smoke`) con `--strict-markers`. Correr todo sin filtros es la regresión completa.
- **Escenarios mínimos obligatorios:** solo votante, jurado en la misma mesa, jurado en otra mesa o puesto, campo vacío, formato inválido y cédula no encontrada.

## Consecuencias

- **A favor:**
  - cada nivel encuentra un tipo distinto de defecto;
  - los selectores por rol hacen que las pruebas fallen también cuando la página pierde accesibilidad;
  - un solo reporte reúne todo (ver [ADR 0016](0016-allure-3-sin-java.md)).
- **En contra:**
  - los escenarios por dos canales duplican los pasos (una implementación por canal);
  - pytest-playwright solo repite por navegador las pruebas que declaran `page`, lo que obligó a una fixture especial para los escenarios BDD de interfaz (caso documentado en `CLAUDE.md`, 2026-11-12).

## Cómo se verifica

- El CI corre los cuatro niveles en cada pull request. Las reglas importantes se comprueban también con pruebas de mutación (ver [ADR 0022](0022-pruebas-de-mutacion.md)).
