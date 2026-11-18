# ADR 0012 · Frontend sin servicios externos: un solo origen, fuente local y mapa ilustrativo

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 y 2026-11-04 (commits `d702ffb` y `050a62d`). El mapa se volvió a evaluar después y se mantuvo
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto

## Contexto

Una aplicación de una sola página suele depender de servicios de terceros: fuentes de Google, mapas, CDNs. Cada uno agrega peticiones a otros dominios, que pueden filtrar datos del visitante (IP, página visitada). También puede fallar o cambiar sin aviso y volver inestables las pruebas. Además, el frontend y la API corren en puertos distintos en desarrollo, y eso exige configurar CORS.

## Decisión

- **Un solo origen en desarrollo:** Vite reenvía `/api` al backend (`API_BASE_URL`). El navegador solo ve el origen del frontend, así que no depende de CORS. Las llamadas HTTP salen únicamente de `services/api.js`.
- **La fuente Inter va instalada en el proyecto** (`@fontsource-variable/inter`), sin peticiones a Google Fonts.
- **Los íconos son SVG descargados del Figma** (`src/assets/iconos/`).
- **El mapa es una ilustración estática** con el aviso "ILUSTRATIVO", sin servicios de mapas. El dueño del producto consideró integrar un servicio de mapas (incluso creó una rama para eso), evaluó alternativas gratuitas y decidió no implementarlo por ahora.
- **Swagger UI también se sirve desde el proyecto**, sin CDN (ver [ADR 0014](0014-swagger-servido-desde-el-proyecto.md)).

## Consecuencias

- **A favor:**
  - ninguna petición del visitante sale a terceros;
  - las pruebas no dependen de servicios externos;
  - en desarrollo no hay que configurar CORS.
- **En contra:**
  - el mapa no es real: solo el plano del puesto de Medellín muestra nombres de calles, y los demás usan el mismo dibujo sin nombres;
  - un despliegue necesitaría su propio proxy o configurar CORS (`CORS_ALLOWED_ORIGINS` ya existe).

## Cómo se verifica

- `tests/e2e/test_swagger_ui.py`: Swagger UI no pide nada a servicios externos.
- `tests/api/test_documentacion_api.py` y `backend/tests/test_documentacion_api.py`: los archivos de Swagger vienen del propio servidor.
- `tests/e2e/test_flujo_consulta.py`: el mapa muestra las calles solo en el puesto que corresponde.
- **Mutaciones verificadas:** Swagger desde un CDN y calles en todos los mapas hacen fallar las pruebas.
