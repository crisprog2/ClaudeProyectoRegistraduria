# ADR 0020 · Reporte publicado en GitHub Pages, con el historial guardado en el propio sitio

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-12 (commit `087d7b1`, PR #5)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto, que aprobó publicar el reporte, y por tanto que sea público, y activó Pages en la configuración del repositorio

## Contexto

El reporte de Allure de cada corrida solo se podía ver descargando un artefacto. Para un portafolio conviene una dirección pública con el último reporte y con las **tendencias**: cuántas pruebas pasan, cuánto tardan y cuáles son inestables a lo largo del tiempo. Para las tendencias, Allure 3 necesita el historial de las corridas anteriores.

## Opciones consideradas

| Opción para el historial | A favor | En contra |
|---|---|---|
| Una rama `gh-pages` con el sitio y el historial | Muy común | Exige permisos de escritura sobre el repositorio y, por lo general, acciones de terceros |
| La caché o los artefactos de GitHub Actions | Sin rama extra | Vencen; se perdería el historial |
| **El historial publicado junto al reporte, y descargado antes de generar el siguiente** | Sin rama extra ni acciones de terceros; el historial nunca vence | Si el sitio no responde, una corrida se genera sin historial |

## Decisión

- **Solo los push a `main` publican.** El trabajo `reporte` descarga `<sitio>/historial/history.jsonl` con `curl -f`; si responde 404 o falla, sigue sin historial y deja un aviso. Después genera el reporte, copia el historial actualizado al sitio y prepara el artefacto de Pages. El trabajo `publicar` lo despliega.
- **Se publica aunque alguna suite falle:** el historial también debe registrar las fallas.
- **Las últimas 30 corridas** (`historyLimit: 30`). Las tendencias se ven en **Report ▾ → Gráficas**.
- **Permisos mínimos:** solo `publicar` tiene `pages: write` e `id-token: write`. No se usa `configure-pages`, para no darle permisos de Pages al trabajo `reporte`.
- **Los pull requests no descargan ni publican el historial.**
- **Desde el 2026-11-17, el sitio incluye también el reporte de cobertura** en `/cobertura/` (ver [ADR 0021](0021-cobertura-con-minimo-del-95.md)).

## Consecuencias

- **A favor:** dirección pública (https://crisprog2.github.io/ClaudeProyectoRegistraduria/) con el último reporte y sus tendencias.
- **Queda público, con la aprobación del dueño del producto:** nombres de pruebas, resultados, versiones, URLs locales del entorno y, en los fallos, capturas y trazas de Playwright. Todo con datos ficticios y sin secretos.
- **Hallazgo:** el primer reporte publicado mostró 577 pruebas en vez de 605 y "14 pruebas repetidas". Así se descubrió que los escenarios BDD de interfaz no se separaban por navegador. Se corrigió en el PR #6 (caso documentado en `CLAUDE.md`).

## Cómo se verifica

- En el sitio publicado: el número de pruebas de la última corrida, "Pruebas repetidas: -" y el historial con una línea por corrida (577 → 605 → 605 → 644).
- Verificado en local: sin archivo previo el reporte se genera bien, y tras tres generaciones el gráfico mostró tres corridas, también servido desde una subcarpeta como la de Pages.
