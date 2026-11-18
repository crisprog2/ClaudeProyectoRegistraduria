# ADR 0008 · La cédula nunca viaja en la URL

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 (commits `cd2027b` y `d702ffb`)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md` y el README
- **Aprobada por:** el dueño del producto

## Contexto

La cédula identifica a una persona. Todo lo que va en una URL queda guardado en muchos lugares: los registros del servidor y de los proxies, el historial y los marcadores del navegador, y la cabecera `Referer` que se envía a otros sitios. Aunque aquí los datos son ficticios, el diseño debe ser el de un sistema real.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| `GET /api/consulta/1098765432/` y `/consulta/resultado?cedula=...` | Más simple; el resultado se puede recargar o compartir | La cédula queda en registros, historiales y en `Referer` |
| **`POST` con la cédula en el cuerpo, y el resultado en el estado de navegación** | La cédula no queda registrada en ninguna URL | El resultado no sobrevive a una recarga y no se puede compartir con un enlace |

## Decisión

- **API:** `POST /api/consulta/` con `{"cedula": "..."}` en el cuerpo, y solo JSON.
- **Frontend:** `ConsultaPage` navega a `/consulta/resultado` con el resultado en el **estado de navegación** (`history.state`), nunca en la ruta ni en los parámetros.
- **Al recargar o entrar directo** al resultado se vuelve a `/consulta`. El navegador conserva `history.state` al recargar, así que `main.jsx` lo borra al cargar la página; si no, el resultado sobreviviría a la recarga.
- **El enlace "Saltar al contenido"** mueve el foco a mano, porque un cambio de `#hash` en la URL borraría el estado de navegación.

## Consecuencias

- **A favor:** la cédula no queda en registros ni historiales.
- **En contra:** no se puede compartir ni guardar el resultado como enlace, y al recargar hay que volver a consultar. Se acepta como el comportamiento correcto para un dato personal.

## Cómo se verifica

- `tests/e2e/test_flujo_consulta.py`: la cédula nunca aparece en la URL, y la recarga y la entrada directa vuelven a la consulta.
- `tests/e2e/test_accesibilidad.py`: "Saltar al contenido" no cambia la URL.
- **Mutaciones verificadas:** poner la cédula en la URL, conservar el estado al recargar y un salto que cambia la URL hacen fallar las pruebas.
