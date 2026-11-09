# Reporte de Allure

Genera un solo reporte con todas las suites de pruebas de ConsultaVoto: backend (white-box), API, BDD y E2E. Usa [Allure 3](https://allurereport.org/docs/v3/), que funciona con Node y no necesita Java.

Cómo correrlo: README de la raíz, paso 9 de "Ejecución".

| Archivo | Para qué sirve |
|---|---|
| `package.json` / `package-lock.json` | Versión exacta del generador (`allure` 3.33.0) y los scripts `generar`, `abrir` y `reporte` |
| `allurerc.mjs` | Nombre del reporte, idioma español, agrupación por nivel y etiquetas ocultas |
| `preparar-resultados.mjs` | Se ejecuta antes de generar: quita las fixtures que terminaron bien y el parámetro interno de pytest-bdd |
| `allure-results/` | Resultados que escribe pytest con `--alluredir=`. No se sube a Git |
| `allure-report/` | Reporte generado, unos 11 MB. No se sube a Git |

Los resultados los produce `allure-pytest`. El plugin [`tests/support/allure_reporte.py`](../tests/support/allure_reporte.py) agrupa las pruebas, registra los pasos de Gherkin y adjunta la evidencia de las pruebas que fallan.
