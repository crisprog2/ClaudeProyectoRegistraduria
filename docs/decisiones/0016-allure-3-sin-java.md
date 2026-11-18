# ADR 0016 · Un solo reporte de Allure 3, sin Java, con solo allure-pytest

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-09 (commit `db6dcd0`, PR #2)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto, que pidió implementar los reportes de Allure

## Contexto

Las cuatro suites (backend, API, BDD y E2E) producían resultados por separado, en la terminal. Para un portafolio hace falta un reporte navegable que muestre todo junto, con la evidencia de cada falla.

## Opciones consideradas

| Tema | Alternativas | Elegida y por qué |
|---|---|---|
| Versión de Allure | Allure 2 (exige Java) o Allure 3 (Node) | **Allure 3:** funciona con Node, que ya está instalado; Java no lo está |
| Integración con pytest-bdd | `allure-pytest-bdd` o los hooks de pytest-bdd | **Solo `allure-pytest` y un plugin propio:** `allure-pytest` y `allure-pytest-bdd` registran los dos la opción `--alluredir`, y pytest no arranca si están instalados juntos. Como el backend comparte el `.venv`, eso lo habría roto también |
| Reporte HTML de pytest | `pytest-html` | Se retiró: no se usaba |

## Decisión

- **Allure 3** (`allure` 3.33.0) en la carpeta `reportes/`, con su propio `package.json`, separado del frontend.
- **Un solo reporte de las cuatro suites,** agrupado por nivel (Backend, API, BDD y E2E). En BDD se agrupa además por canal ("Por la API" o "Por la interfaz") y por feature.
- **El plugin `tests/support/allure_reporte.py`:**
  - registra cada paso de Gherkin;
  - marca como críticas las pruebas `smoke`;
  - **adjunta la evidencia de cada falla:** la petición y la respuesta de la API, o la URL, la captura y la traza de Playwright;
  - escribe el entorno (versiones y URLs) sin secretos.
- **`reportes/preparar-resultados.mjs`** quita antes de generar las fixtures que terminaron bien (unas 13 000 por corrida) y un parámetro interno de pytest-bdd que Allure 3 no oculta.
- **Privacidad:** las etiquetas `host` y `thread` se ocultan porque muestran el nombre del equipo, y el visor local escucha solo en `127.0.0.1`.
- **`--alluredir=` siempre con signo igual:** con un espacio y la carpeta ya creada, pytest toma la ruta como un argumento de pruebas y el backend pierde su `pytest.ini`.

## Consecuencias

- **A favor:** un reporte único con la evidencia necesaria para entender una falla sin volver a correrla, sin instalar Java.
- **En contra:**
  - el plugin propio usa un atributo privado de pytest-playwright para la traza; si se actualiza pytest-playwright, hay que revisarlo;
  - un nivel nuevo de pruebas necesita su grupo en el plugin.

## Cómo se verifica

- Se comprobó con dos pruebas temporales que fallaban a propósito: se adjuntaron la petición y la respuesta 404 en la de API, y la URL, la captura y la traza en la de interfaz. Se borraron después.
- El reporte se genera en cada corrida del CI y el de `main` se publica (ver [ADR 0020](0020-reporte-publicado-con-historial.md)).
