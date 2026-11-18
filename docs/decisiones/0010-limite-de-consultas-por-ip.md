# ADR 0010 · Límite de consultas por IP, sin confiar en `X-Forwarded-For`

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 (commit `cd2027b`). El límite se volvió configurable después
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md` y `backend/config/settings/base.py`
- **Aprobada por:** el dueño del producto

## Contexto

La consulta es pública y no exige sesión. Sin un límite, alguien podría recorrer cédulas una tras otra para averiguar quién está registrado y dónde vota.

DRF identifica al cliente de un límite por su IP. Con su configuración por defecto (`NUM_PROXIES = None`), toma esa IP de la cabecera `X-Forwarded-For`, que **cualquier cliente puede inventar**: bastaría con cambiarla en cada petición para no llegar nunca al límite.

## Decisión

- **Límite de 30 consultas por minuto por IP**, configurable con `CONSULTA_LIMITE_POR_MINUTO` (un entero mayor que 0; vacío vale 30). Al superarlo se responde 429 `DEMASIADAS_CONSULTAS`, con `Retry-After`.
- **`NUM_PROXIES = 0`:** el cliente se identifica por `REMOTE_ADDR`, la dirección real de la conexión, que no se puede falsificar desde una cabecera. Si se despliega detrás de un proxy, este valor debe ser el número de proxies de confianza.
- **Las pruebas black-box levantan el servidor con un límite alto (1000)**, porque hacen muchas consultas seguidas. El 429 se prueba en white-box, donde `settings/test.py` fija el límite en 30 para que no dependa del `.env`.
- **El mismo criterio se aplicó en la fase 1** al límite de intentos de inicio de sesión (5 por minuto, `INGRESO_LIMITE_POR_MINUTO`; ver [ADR 0002](0002-tokens-en-memoria-y-cookie-httponly.md)).

## Consecuencias

- **A favor:** recorrer cédulas en masa se vuelve lento, y el límite no se puede evadir con una cabecera.
- **En contra:**
  - varios usuarios detrás de una misma IP (una red corporativa) comparten el límite;
  - el contador vive en la caché de Django, así que con varios servidores cada uno tendría el suyo, y haría falta una caché compartida.

## Cómo se verifica

- `backend/tests/test_api_consulta.py`: la consulta número 31 recibe 429 con `Retry-After`, y falsificar `X-Forwarded-For` no evade el límite.
- `backend/tests/test_documentacion_api.py`: el 429 real coincide con el documentado en Swagger.
- `backend/tests/test_configuracion.py`: valores válidos e inválidos de la variable (`0`, `abc`, `10/min`…).
- **Mutación verificada:** con el valor por defecto de `NUM_PROXIES`, la prueba de `X-Forwarded-For` falla.
