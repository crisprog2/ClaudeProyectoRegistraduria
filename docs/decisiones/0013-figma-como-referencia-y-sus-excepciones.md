# ADR 0013 · El Figma como referencia, y cuándo apartarse de él

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 a 2026-11-04 (commits `b801900`, `d702ffb`, `050a62d` y `516de27`)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto

## Contexto

Las pantallas se diseñaron en Figma: consulta, tres estados de error, resultado de votante y resultado de jurado, todas a 1440 px. Al implementarlas aparecieron casos que el Figma no cubría y algún valor del diseño que no cumplía las normas de accesibilidad. Había que decidir qué hacer en cada caso.

## Decisión

**El Figma es la referencia.** Cada fase del frontend se revisó con capturas de Playwright a 1440 px, comparadas con el diseño. Se aparta de él solo en estos casos, todos aprobados:

| Caso | Decisión | Motivo |
|---|---|---|
| Aviso del votante | Texto neutro: "Eres votante y no tienes designación como jurado" | No depende del género de la persona |
| Edad | Solo en la pantalla del votante | Así está en el Figma; la API la devuelve siempre y el frontend decide |
| Textos del jurado en otra mesa y en otro puesto | Textos propios en `utils/textosJurado.js` | El Figma solo diseña "misma mesa"; los otros dos los aprobó el dueño del producto |
| Errores 429 y servidor caído | Reutilizan el panel de "cédula no encontrada" con su propio texto | No están diseñados |
| Color del placeholder | `#66778b` (contraste 4.59:1) en lugar de `#8a9bb0` (2.84:1) | El del Figma no cumple WCAG AA |
| Pantallas pequeñas | Criterio propio: columnas apiladas desde 1100 px, reorganización a 768 px y tamaños menores a 600 y 480 px | El Figma solo diseña 1440 px |
| Página 404 | Reutiliza el layout, `PageHeading` y `Card` | No está diseñada |
| "Cómo consultar" y "Ayuda" | Enlaces solo visuales, que no se pueden enfocar | Están en el Figma, pero no tienen página |
| Pantallas de roles (fases 5 a 7) | Las diseña Claude con el estilo actual y el dueño las aprueba por capturas | No hay cupo en el MCP de Figma; se podrán ajustar cuando vuelva |

Además:
- **Accesibilidad por encima del diseño:** enlace "Saltar al contenido", título de pestaña por pantalla y foco en el título al cambiar de pantalla.
- **El frame del jurado se implementó desde una captura**, porque el MCP de Figma agotó su cupo el 2026-11-03. Los textos son exactos; algunas medidas y colores son aproximados y conviene compararlos cuando haya cupo.

## Consecuencias

- **A favor:** la interfaz es fiel al diseño donde existe y accesible donde el diseño no alcanzaba (0 violaciones de axe en las 8 pantallas).
- **En contra:** las diferencias con el Figma deben quedar registradas (en `CLAUDE.md` y aquí), para que nadie las "corrija" de vuelta.

## Cómo se verifica

- `tests/e2e/test_accesibilidad.py`: axe-core (WCAG 2.1 A y AA) en las 8 pantallas, títulos de pestaña, foco y "Saltar al contenido".
- `tests/e2e/test_pantallas_pequenas.py`: sin desborde horizontal de 1440 a 320 px.
- `tests/e2e/test_flujo_consulta.py`: la edad solo para el votante y los textos de los tres casos de jurado.
- **Mutaciones verificadas:** edad visible para el jurado, contraste bajo y la navegación sin `flex-wrap` (solo falla a 320 px) hacen fallar las pruebas.
