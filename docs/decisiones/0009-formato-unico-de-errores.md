# ADR 0009 · Un solo formato de error: `{"codigo", "mensaje"}`

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 (commit `cd2027b`). Se amplió en la fase 1 de roles (2026-11-18)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md` y `backend/apps/consultas/exceptions.py`
- **Aprobada por:** el dueño del producto

## Contexto

Cada parte de la pila produce errores con su propio formato:
- Django REST Framework responde `{"detail": "..."}`;
- un error de validación devuelve una lista de mensajes por campo;
- los errores de protocolo (método no permitido, cuerpo que no es JSON) tienen sus propios textos en inglés.

El frontend tendría que entender cada formato, y las pruebas dependerían de textos que pueden cambiar.

## Decisión

- **Todas las respuestas de error tienen la forma `{"codigo", "mensaje"}`:**
  - `codigo` es estable (`CEDULA_REQUERIDA`, `CEDULA_FORMATO_INVALIDO`, `CEDULA_NO_ENCONTRADA`, `SOLICITUD_INVALIDA`, `METODO_NO_PERMITIDO`, `DEMASIADAS_CONSULTAS`…). El frontend y las pruebas se basan en él.
  - `mensaje` es el texto para el usuario. Para los errores de la consulta, son **los textos del Figma**.
- **Un manejador central** (`apps/consultas/exceptions.manejador_de_errores`, el `EXCEPTION_HANDLER` de DRF) traduce cualquier error. Conserva el código HTTP y las cabeceras de DRF, como `Retry-After` o `Allow`.
- **La validación no depende de DRF:** `validators.validar_cedula()` lanza un `ValidationError` de Django con su código, y el manejador lo traduce.
- **Un error no controlado devuelve `None`:** Django responde 500 sin exponer detalles internos.
- **Ampliación de la fase 1 (2026-11-18):** el manejador elige el código en este orden:
  1. el código propio de la excepción;
  2. los textos propios de la vista (`errores_drf`), para mensajes distintos por ruta;
  3. los comunes;
  4. `ERROR_DE_SOLICITUD`.

## Consecuencias

- **A favor:** un solo contrato de errores para el frontend, Swagger y las pruebas, y los textos viven en un solo lugar. La documentación de Swagger los toma del código para no repetirlos.
- **En contra:** cada error nuevo necesita su código y su mensaje en el manejador o en su excepción.

## Cómo se verifica

- `backend/tests/test_api_consulta.py` y `backend/tests/test_manejador_errores.py`: cada error con su código y su mensaje exactos, y el orden de elección.
- `tests/api/test_validaciones_cedula.py` y `test_protocolo_http.py`: los mismos códigos contra el servidor real, con los mensajes de `tests/data/mensajes_error.json`.
- `tests/api/test_documentacion_api.py`: los ejemplos de error de Swagger usan los mensajes reales.
