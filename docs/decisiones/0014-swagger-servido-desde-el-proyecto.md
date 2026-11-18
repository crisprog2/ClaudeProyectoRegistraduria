# ADR 0014 · Documentación OpenAPI 3.1 con Swagger UI servido desde el proyecto, y probada

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-06 (commit `7396f61`, PR #1)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto, que pidió implementar Swagger

## Contexto

La API necesitaba documentación interactiva para probarla sin escribir código y para importarla en Postman. Una documentación que no se prueba termina desactualizada: describe campos que ya no existen o ejemplos que ya no responden lo que dicen.

## Opciones consideradas

| Tema | Alternativas | Elegida y por qué |
|---|---|---|
| Generador | Escribir el YAML a mano; drf-yasg (OpenAPI 2); drf-spectacular | **drf-spectacular:** genera OpenAPI 3 desde los serializadores reales, así que la documentación no se separa del código |
| Versión | OpenAPI 3.0 o 3.1 | **3.1:** usa JSON Schema estándar, así que las pruebas validan las respuestas sin convertir el esquema |
| Archivos de Swagger UI | Desde un CDN o desde el proyecto | **Desde el proyecto** (drf-spectacular-sidecar): sin peticiones a terceros (ver [ADR 0012](0012-frontend-sin-servicios-externos.md)) |

## Decisión

- **Rutas:** `/api/docs/` (Swagger UI) y `/api/schema/` (YAML por defecto, JSON con `?format=json`).
- **Siempre activa:** la API ya es pública y los datos son ficticios. Si se desplegara en un servidor público, habría que revisarlo.
- **La documentación sale del código:**
  - la respuesta, de los serializadores reales (`JuradoSerializer` declara sus campos para que el esquema los vea);
  - los mensajes de error, de los módulos que los producen (`esquema.py` no repite textos).
- **Los docstrings de los serializadores se publican en Swagger;** las notas internas van en comentarios.
- **La documentación se prueba:**
  - la especificación es válida y sin advertencias;
  - las respuestas reales cumplen el esquema, marcado con `additionalProperties: false` (OpenAPI admite campos no documentados por defecto);
  - los ejemplos documentados coinciden con lo que responde la API;
  - cada código HTTP real está documentado.
- **Hallazgo:** un `DJANGO_DEBUG=` vacío apagaba `DEBUG` y Swagger se veía en blanco, porque Django no servía sus archivos estáticos. Se corrigió `env_bool` para que una variable vacía use el valor por defecto.

## Consecuencias

- **A favor:** si la API cambia sin actualizar la documentación, el CI falla.
- **En contra:** con `DEBUG=False`, Swagger se ve en blanco; un despliegue necesitaría `collectstatic` y un servidor de archivos estáticos.

## Cómo se verifica

- `backend/tests/test_documentacion_api.py`: especificación válida sin advertencias, OpenAPI 3.1, sin CDN, y el 429 real contra el documentado.
- `tests/api/test_documentacion_api.py`: las respuestas de todos los casos de `tests/data/` cumplen la especificación, incluidas las de la sesión (fase 1).
- `tests/e2e/test_swagger_ui.py`: Swagger UI carga sin servicios externos, y "Try it out" ejecuta una consulta real.
- **Mutaciones verificadas:** campo sin documentar, tipo distinto del real, código o ejemplo faltante, ejemplo desactualizado, mensaje cambiado, Swagger desde un CDN y sin `Retry-After`.
