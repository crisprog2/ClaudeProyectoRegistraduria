# CLAUDE.md

Contexto y convenciones para futuras sesiones de trabajo en este repositorio.

## Contexto

Proyecto de **portafolio de un Quality Engineer**. El objetivo principal es mostrar buenas prácticas de QA y automatización de pruebas sobre una app web full stack; la app en sí es el sistema bajo prueba.

**ConsultaVoto** es una app **ficticia** de consulta electoral:
- El usuario ingresa su número de cédula.
- Se muestra su lugar de votación: puesto, dirección, ciudad, departamento y mesa.
- Si fue designado jurado, se muestra además su asignación: rol (p. ej. "Jurado titular"), puesto, dirección y mesa de servicio, que **pueden ser distintos** a donde vota.
- Casos de error: campo vacío, formato inválido y cédula no encontrada.

## Reglas de marca y datos (no negociables)

- Marca ficticia: **ConsultaVoto** — subtítulo "Proyecto de portafolio QA". **No** usar "Registraduría Nacional del Estado Civil" ni ningún nombre o logo de entidades reales.
- El sitio no debe parecer oficial: siempre visibles el `DemoBanner`, el badge "DATOS FICTICIOS" y los avisos de prototipo.
- Solo datos inventados. Nunca cédulas, nombres o direcciones reales.

## Stack

- **Backend**: Python 3.11 + Django 5.2 LTS + Django REST Framework + MySQL 8.0. No subir a Django 6: exige Python 3.12+.
- **Documentación de la API**: drf-spectacular (OpenAPI 3.1) y Swagger UI servido desde el proyecto con drf-spectacular-sidecar.
- **Entorno**: un solo entorno virtual en la raíz (`.venv/`) para backend y pruebas. Versiones fijadas con `==` en `backend/requirements.txt` y `tests/requirements.txt`. Navegadores de Playwright (Chromium, Firefox, WebKit) instalados fuera del repo.
- **Base de datos**: servidor MySQL 8.0 **local** del usuario (servicio de Windows, puerto 3306). No se usa Docker. En CI se usa el contenedor `mysql:8.0` como servicio de GitHub Actions para mantener la misma versión mayor.
- **Controlador de MySQL**: PyMySQL, registrado como `MySQLdb` en `backend/config/__init__.py`, en local y en CI. mysqlclient se retiró porque el Control inteligente de aplicaciones de Windows 11 bloqueó su componente compilado, que no tiene firma digital. Django no soporta PyMySQL oficialmente: lo respaldan las pruebas. La conexión local sale cifrada con TLS, así que `caching_sha2_password` funciona sin instalar `cryptography`.
- **Frontend**: React + Vite + react-router-dom.
- **Pruebas** (todas en Python):
  - `backend/tests/` — white-box, pytest + pytest-django.
  - `tests/api/` — black-box de la API, pytest + requests.
  - `tests/bdd/` — pytest-bdd, Gherkin **en español** (`# language: es`).
  - `tests/e2e/` — Playwright para Python (pytest-playwright).
- **Reportes**: Allure 3 (`reportes/`, Node) con resultados de `allure-pytest`. Ver la sección "Reporte de Allure".
- **Cobertura**: pytest-cov (coverage.py) sobre el backend, con ramas y un mínimo del 95 %. Ver la sección "Cobertura de código".
- **Autenticación**: JWT con djangorestframework-simplejwt 5.5.1 (PyJWT 2.15.1), token de refresco en una cookie HttpOnly, roles con los grupos de Django. Ver la sección "Autenticación y roles".
- **CI**: GitHub Actions en `.github/workflows/ci.yml`, que llama a `scripts/pruebas.py`. Ver la sección "Integración continua".

## Diseño (Figma)

Figma: https://www.figma.com/design/olhIBoGbGoNDJ9LBxbxiqz/Proyecto-Registraduria (fileKey `olhIBoGbGoNDJ9LBxbxiqz`). Accesible con el servidor MCP de Figma (alcance user): **lectura y edición funcionan**, pero el plan Starter tiene un límite de llamadas (ver "Estado"). Antes de editar con `use_figma` cargar las guías `figma-use` y `figma-generate-design`. El archivo no tiene variables, estilos ni componentes: se reutilizan los valores de las pantallas existentes (Inter; textos `#142c43` / `#53677b`; bordes `#dce4ed` / `#9aabbe`; azul `#1658c1`; rojo `#c9454c`).

Frames (página `0:1`):
- `6:2319` Consulta electoral · Inicio
- `17:2` Consulta electoral · Error campo vacío
- `17:145` Consulta electoral · Error formato inválido
- `17:288` Consulta electoral · Cédula no encontrada
- `6:2442` Resultado · Votante sin designación
- `6:2609` Resultado · Votante y jurado

Pantallas y componentes:
1. **Consulta** (`/consulta`): encabezado, `CedulaForm`, `PromoPanel` ("Tu voz cuenta"), `PasosConsulta`. Estados de error **debajo del campo, en lugar del texto de ayuda**:
   - Campo vacío → `FormError`: borde rojo + "Ingresa tu número de cédula para consultar."
   - Formato inválido → `FormError`: borde rojo + "El número no es válido. Escribe solo números, sin puntos, espacios ni comas."
   - No encontrada → `ConsultaSinResultado`: panel rojo claro, borde normal en el campo, "No encontramos información para esta cédula" + "Verifica el número e inténtalo de nuevo. Solo existen cédulas de ejemplo."
2. **Resultado** (`/consulta/resultado`): `CiudadanoResumen`, `LugarVotacionCard`, `MapaPuesto` y además:
   - **Solo votante:** `VotanteAlert` (badge VOTANTE) y `ConsejoVotacion` ("Antes de ir a votar"). `CiudadanoResumen` muestra la edad.
   - **Jurado:** `JuradoAlert` (badge JURADO), `AsignacionJuradoCard` y `ResponsabilidadesNota`.

Layout común: `TopBar`, `SiteHeader`, `MainNav`, `FlagStripe`, `DemoBanner`, `Breadcrumb`, `Stepper`, `SiteFooter`.

Bases compartidas agregadas al implementar (no son nodos del Figma): `AvisoCondicion` (`VotanteAlert` y `JuradoAlert`), `TarjetaMesa` (`LugarVotacionCard` y `AsignacionJuradoCard`) y `NotaDestacada` (`ConsejoVotacion` y `ResponsabilidadesNota`).

## Decisiones tomadas

- Un ciudadano que **no es jurado** es solo votante: el resultado muestra el aviso `VotanteAlert` con el texto **neutro** "Eres votante y no tienes designación como jurado" (no depende del género), el lugar de votación y el consejo "Antes de ir a votar". Las pruebas deben verificar la **presencia** de ese aviso y la **ausencia** de las secciones de jurado.
- La pantalla del votante muestra la **edad** ("Edad · 32 años"); la del jurado no (así está en el Figma). La API devuelve la edad en ambos casos y el frontend decide si la muestra.
- "Cómo consultar" y "Ayuda" en `MainNav` son **enlaces solo visuales**; no tienen página.
- La cédula viaja por **estado de navegación**, nunca en la URL.
- La cédula se ingresa solo con dígitos y se **muestra formateada** con puntos (`1.098.765.432`).
- Los estados de error (`FormError`, `ConsultaSinResultado`) están diseñados en Figma (frames `17:2`, `17:145`, `17:288`). El mensaje de formato inválido no menciona la longitud hasta que se defina la regla de la cédula.
- **Roles (2026-11-18):** Ciudadano (sin cuenta), Administrador y Analista. La administración es una pantalla propia; el admin de Django queda solo para el superusuario. Detalles en "Autenticación y roles" y en `docs/decisiones/`.
- **`backend/apps/consultas/models.py` es del usuario.** Lo escribió el usuario y se ajustó con revisión de Claude. Cualquier cambio estructural al modelo se propone y se aplica solo con su aprobación.

## Modelo de datos

`backend/apps/consultas/models.py` (diagrama ER en el README):

- `Departamento` (PK `cod_departamento`, 2 car.) → `Ciudad` (PK `cod_ciudad`, 5 car.) → `PuestoVotacion` (PK `cod_puesto`, ≤10 car.) → `Mesa` (PK `cod_mesa` autoincremental, `numero` único por puesto).
- `Persona` (PK `cedula` CharField ≤10, solo dígitos) → `mesa` donde vota.
- `DesignacionJurado`: OneToOne `persona` (`related_name='designacion_jurado'`), `mesa_servicio` y `rol` (`TITULAR` / `REMANENTE`).
- Relaciones inversas: `departamento.ciudades`, `ciudad.puestos`, `puesto.mesas`, `mesa.votantes`, `mesa.jurados`.

Reglas:
- Es jurado ⇔ existe `DesignacionJurado` (`hasattr(persona, 'designacion_jurado')`). No hay campo booleano.
- El puesto, la dirección, la ciudad y el departamento de servicio se obtienen de `mesa_servicio.puesto`; no se duplican.
- `nombre_completo` es una propiedad del modelo (omite segundo nombre/apellido vacíos); el admin y la API la reutilizan.
- `edad` no se guarda: es una propiedad calculada desde `fecha_nacimiento`. En pruebas usar `calcular_edad(fecha_referencia)` para que el resultado no dependa del día en que se ejecuta.
- `PROTECT` en todas las FK de referencia; solo `DesignacionJurado.persona` usa `CASCADE`.
- `segundo_nombre` y `segundo_apellido` son opcionales; `genero` admite `F`, `M` u `O`.
- La validación de formato de la cédula (solo dígitos, longitud) va en `validators.py`, no en el modelo.

Convenciones del modelo:
- Campos en snake_case; las FK se nombran como el objeto (`departamento`, `puesto`, `mesa`) y usan `db_column='cod_*'`.
- El nombre visible de cada entidad es `nombre` (no repetir el nombre del modelo).
- Docstring por modelo con la lista de campos. Indentación de 4 espacios (PEP 8).
- `__str__` legible, sin IDs internos: `Mesa 018 · Colegio Cívico La Esperanza`, `Jurado titular · Carlos Martínez · Mesa 018 · Colegio Cívico La Esperanza`. Los de `Mesa` y `DesignacionJurado` leen modelos relacionados: en listados usar `select_related`. Cambiar un `__str__` no genera migración.

## Admin de Django

`backend/apps/consultas/admin.py` registra los 6 modelos para revisar los datos de demostración. Desde la fase 1, el admin solo admite al superusuario (`apps/cuentas/sitio_admin.py`, ADR 0003):
- Listados con `list_select_related` (sin consultas por fila) y `autocomplete_fields` para las relaciones (el admin relacionado debe tener `search_fields`).
- `PersonaAdmin`: columnas de edad calculada, puesto y "es jurado"; filtro propio `EsJuradoFilter` (sí/no); la designación se edita en la misma ficha (`DesignacionJuradoInline`, máximo 1).
- `DesignacionJuradoAdmin`: columna "vota en la misma mesa".

## API REST de consulta

`POST /api/consulta/` con `{"cedula": "..."}` (la cédula nunca va en la URL). Capas:
- `validators.validar_cedula()`: quita espacios externos; exige texto de **6 a 10 dígitos ASCII sin 0 inicial**. Lanza `django.core.exceptions.ValidationError` con código `CEDULA_REQUERIDA` o `CEDULA_FORMATO_INVALIDO` (no depende de DRF).
- `services.consultar_por_cedula()`: una sola consulta SQL (`select_related`, incluida la designación); lanza `CedulaNoEncontrada`.
- `serializers.ResultadoConsultaSerializer`: `ciudadano` (cedula, nombre_completo, edad), `lugar_votacion` (mesa, puesto, direccion, ciudad, departamento) y `jurado` (rol, rol_display, ubicación de la mesa de servicio, misma_mesa) o `null`. La edad usa `timezone.localdate()`. Nunca expone género, fecha de nacimiento ni IDs internos.
- `views.ConsultaView`: solo POST, solo JSON, sin autenticación (por eso sin CSRF), límite `ConsultaRateThrottle`.
- `exceptions.manejador_de_errores` (EXCEPTION_HANDLER): todas las respuestas de error son `{"codigo", "mensaje"}`.

| HTTP | `codigo` |
|---|---|
| 400 | `CEDULA_REQUERIDA`, `CEDULA_FORMATO_INVALIDO`, `SOLICITUD_INVALIDA` (JSON mal formado o que no es objeto) |
| 404 | `CEDULA_NO_ENCONTRADA` |
| 405 | `METODO_NO_PERMITIDO` |
| 415 | `SOLICITUD_INVALIDA` (no es JSON) |
| 429 | `DEMASIADAS_CONSULTAS` (más de `CONSULTA_LIMITE_POR_MINUTO`/min por IP, 30 por defecto; incluye `Retry-After`) |

Los mensajes son los textos del Figma. Seguridad: `NUM_PROXIES = 0` hace que el límite use `REMOTE_ADDR`; con el valor por defecto de DRF se podría evadir falsificando `X-Forwarded-For` (hay una prueba que lo verifica).

Límite configurable: `CONSULTA_LIMITE_POR_MINUTO` (entero > 0; vacío = 30). La suite black-box levanta el servidor con un valor alto (1000) porque hace ~60 peticiones seguidas. `settings/test.py` lo fija en 30 para que las pruebas del 429 no dependan del `.env`. El 429 solo se prueba en white-box.

Documentación: `/api/docs/` (Swagger UI) y `/api/schema/` (OpenAPI; YAML por defecto, JSON con `?format=json`).
- `apps/consultas/esquema.py` describe el endpoint con `@documentar_consulta`: ejemplos, códigos HTTP y cabeceras. Toma los mensajes de `validators.py`, `services.py` y `exceptions.py` para no repetirlos. Sus serializadores `SolicitudConsultaSerializer` y `ErrorSerializer` solo documentan.
- La respuesta sale de los serializadores reales: `JuradoSerializer` declara sus campos, sin `to_representation`, para que el esquema los vea.
- Los docstrings de los serializadores se publican en Swagger: las notas internas van en comentarios.
- Está siempre activa porque la API ya es abierta y los datos son ficticios; revisarlo si se despliega en un servidor público. Con `DEBUG=False` la página responde, pero Django no sirve sus archivos estáticos y se ve en blanco: un despliegue necesitaría `collectstatic` y un servidor de estáticos.

Pruebas white-box (`backend/tests/`, 228): `test_autenticacion.py`, `test_roles_y_permisos.py` y `test_usuarios_demo.py` (ver "Autenticación y roles"), `test_admin.py` (listados, filtro "es jurado", columnas calculadas y consultas por fila; ver "Cobertura de código"), `test_manejador_errores.py`, `test_models.py` (`nombre_completo` y días límite de `calcular_edad`), `test_validators.py`, `test_services.py` (incluye "exactamente 1 consulta SQL"), `test_api_consulta.py` (JSON exacto de los casos del Figma, todos los errores, límite de consultas y X-Forwarded-For), `test_documentacion_api.py` (especificación válida y sin advertencias, sin CDN y 429 real contra el documentado) y `test_configuracion.py` (`env_bool` y controlador PyMySQL). `conftest.py`: `datos_demo`, `fecha_fija` (edad estable), `limpiar_cache` (autouse: el contador del límite vive en la caché), `consultar`, `crear_usuario` (con `CONTRASENA_PRUEBA`, que solo existe en la base de pruebas), `ingresar` y `cabecera_app`. Se ejecutan con `cd backend; pytest`.

Pruebas black-box de la API (`tests/api/`, 144, marker `api`; incluye `test_autenticacion.py`, ver "Autenticación y roles"): pytest + requests contra el servidor en ejecución, sin importar nada de Django.
- `test_consulta_cedula.py`: respuesta exacta de los 10 ciudadanos del fixture, reglas de los escenarios mínimos (misma mesa, otra mesa del mismo puesto, otro puesto, solo votante), espacios externos, contrato de claves y que no se expongan datos sensibles.
- `test_validaciones_cedula.py`: 19 casos de cédula requerida, formato inválido y no encontrada, con código y mensaje exactos.
- `test_protocolo_http.py`: 405 (con cabecera `Allow`), 415 y JSON que no es objeto.
- `test_documentacion_api.py`: las respuestas reales de todos los casos de `tests/data/` cumplen la especificación, y los ejemplos documentados coinciden con lo que responde la API. `support/openapi.py` marca cada objeto con `additionalProperties: false`, porque OpenAPI admite campos no documentados por defecto. El 429 se comprueba en white-box. Los archivos estáticos de Swagger exigen un servidor con `DEBUG` activo.
- Soporte en `tests/support/`: `config.py` (`API_BASE_URL` del `.env`), `api_client.py` (`ConsultaApiClient`; guarda `ultima_respuesta` para el reporte de Allure), `data_loader.py` (`cargar`, `caso`, `como_parametros`: el campo `"smoke": true` de un caso agrega el marker) y `edad.py` (oráculo de edad independiente del backend, con la fecha de America/Bogota).
- Datos en `tests/data/`: `ciudadanos.json`, `cedulas_invalidas.json`, `solicitudes_invalidas.json`, `mensajes_error.json` y `contrato_consulta.json`.
- `pytest.ini` de la raíz agrega `pythonpath = tests` (imports `support.*`). Si no hay servidor, el fixture `api` detiene la corrida con instrucciones.
- Mutación verificada: exponer `genero` y aceptar 0 inicial hacen fallar la suite. También se detectan en la documentación: campo sin documentar, tipo distinto del real, código o ejemplo faltante, ejemplo desactualizado, mensaje cambiado, Swagger desde un CDN, nombre de la entidad real, sin aviso de datos ficticios y sin `Retry-After`.
- El fixture `api` (cliente compartido por API y BDD) está en `tests/conftest.py`. Si no hay servidor, detiene la corrida con instrucciones.

Pruebas BDD (`tests/bdd/`, tag `@bdd`; 21 escenarios por la API y 14 por la interfaz en cada navegador): 4 features en lenguaje de negocio, sin HTTP ni pantallas. Los mismos features se ejecutan por dos canales: `step_defs/api/` (marker `api`) y `step_defs/interfaz/` (marker `e2e`). Cada carpeta tiene su `conftest.py` y su `common_steps.py`, porque los textos de los steps son iguales y sus implementaciones no deben mezclarse.
- `consulta_lugar_votacion.feature`: solo votante y cédula con espacios externos.
- `consulta_jurado.feature`: jurado en la misma mesa, en otra mesa del mismo puesto y en otro puesto.
- `validaciones_cedula.feature`: sin cédula, esquema de formato inválido (7 ejemplos) y no registrada.
- `inicio_sesion.feature` (fase 1, **solo por la API** hasta la fase 5): inicio de sesión por rol (esquema con 2 ejemplos), contraseña incorrecta, usuario inexistente, sin datos, la sesión se renueva y cerrar sesión. Sus steps están en `step_defs/api/test_inicio_sesion.py` y usan la fixture `cliente_sesion`.
- Los "Dado" describen el tipo de ciudadano y toman el caso de `tests/data/ciudadanos.json`. Los mensajes del Figma y los ejemplos de cédulas inválidas van literales en el feature porque son la especificación.
- El estado viaja entre steps en fixtures con `target_fixture` (`ciudadano` y, en la API, `respuesta`). En la interfaz, el estado es la propia página, a través de los Page Objects.
- El feature usa el mensaje de la API ("No encontramos información para esta cédula."); el panel del Figma lo muestra sin punto, así que el step de interfaz ignora el punto final.
- Los casos de protocolo (405, 415, JSON mal formado) no van en Gherkin: solo en `tests/api/`.
- Mutación verificada: si el serializer omite la designación fallan los 3 escenarios de jurado; si se acepta el 0 inicial falla su ejemplo.
- **Un escenario por navegador:** `step_defs/interfaz/conftest.py` tiene la fixture automática `_un_escenario_por_navegador(page)`. Hace que cada escenario de interfaz se recoja una vez por cada `--browser` (`[chromium]`, `[firefox]`, `[webkit]`), como las E2E. No quitarla: ver el caso siguiente.

#### Caso resuelto: los escenarios BDD de interfaz no se separaban por navegador (2026-11-12)

- **Cómo se detectó:** al revisar el primer reporte publicado en GitHub Pages (https://crisprog2.github.io/ClaudeProyectoRegistraduria/). Mostraba 577 pruebas en vez de 605, el grupo BDD tenía 28 resultados en vez de 56, y aparecían "14 pruebas repetidas".
- **Causa:** pytest-playwright repite una prueba por navegador en `pytest_generate_tests`, y solo lo hace si `page`, `browser_name` u otra fixture del navegador forma parte de las fixtures que la prueba declara. Las funciones de prueba que genera pytest-bdd no declaran `page`: cada step la obtiene al ejecutarse, a través de los Page Objects `consulta` y `resultado`. Por eso los 14 escenarios se recogían una sola vez, sin `[navegador]` en el nombre, y la fixture `browser_name` devolvía el primer `--browser`. Con más de uno, pytest-playwright lo avisa con el warning "When using unittest.TestCase specifying multiple browsers is not supported" (el "1 warning" que salía en las corridas con varios navegadores).
- **Consecuencias:**
  - **En local, con varios navegadores a la vez** (`pytest tests/bdd tests/e2e -m e2e --browser chromium --browser firefox --browser webkit` o `scripts/pruebas.py interfaz` con varios `--browser`), los escenarios BDD solo corrían en el primero. Las E2E sí corrían en todos.
  - **En el CI** sí corrían en los tres navegadores, porque cada trabajo usa uno solo. Pero el resultado no llevaba el navegador como parámetro: los tres trabajos producían el mismo `historyId`, y Allure los juntaba como repeticiones de una misma prueba.
  - **Lo verificado antes sigue siendo válido:** la afirmación "14 casos BDD pasan en Chromium, Firefox y WebKit" se comprobó con una corrida separada por navegador.
- **Corrección:** la fixture automática `_un_escenario_por_navegador(page)`. Al depender de `page`, pytest-playwright la ve al recoger las pruebas y repite cada escenario por navegador. Devuelve la misma página que usan los Page Objects; no abre otra. Solo está en `step_defs/interfaz/`, porque los escenarios por la API no usan navegador. Además, `environment.properties` ya no incluye "Navegadores": en el CI cada trabajo escribía el suyo y quedaba solo el último. Cada prueba de interfaz ya muestra su navegador como parámetro.
- **Verificación (en local):**
  - Con 1, 2 y 3 navegadores se recogen 14, 28 y 42 escenarios de interfaz. Los de la API siguen siendo 14.
  - `pytest tests/bdd -m e2e --browser chromium --browser firefox --alluredir=...` dio 28 resultados con 28 `historyId` distintos y el parámetro `browser_name`, sin el warning.
  - `python scripts/pruebas.py todo --allure --browser chromium --browser firefox` pasó: 97 + 124 + 256 pruebas, y 477 resultados en Allure (BDD 42 = 14 por la API + 14 por navegador), sin repetidos.
- **Mutación verificada:** sin el decorador de la fixture vuelven los 14 escenarios con dos navegadores, el warning y la ejecución en un solo navegador.
- **Verificación en el CI (PR #6, corrida sobre `main` 43243179420):** pasaron todos los trabajos. El reporte publicado muestra 605 resultados, ninguna prueba repetida y el commit `54b39fc`.
- **Si reaparece:** el warning "specifying multiple browsers is not supported", o un grupo BDD con menos de 14 × navegadores + 14 resultados en el reporte, indican que alguna prueba que usa el navegador no declara `page`.

Pruebas E2E (`tests/e2e/`, 114 casos, marker `e2e`): Playwright contra el backend y el frontend en marcha, en Chromium, Firefox y WebKit. Cubren lo que los features no describen.
- `test_flujo_consulta.py`: formato de cédula y mesa, edad solo para el votante, textos de los 3 casos de jurado, mapa, la cédula nunca en la URL, recarga y entrada directa, 404, avisos obligatorios y ninguna mención de entidades reales.
- `test_casos_error.py`: errores del campo (que no llaman a la API), no encontrada y, simulados interceptando la petición con `page.route`, 429, conexión caída y error 500.
- `test_accesibilidad.py`: axe-core (`axe-playwright-python`, WCAG 2.1 A/AA y buenas prácticas) en las 8 pantallas, títulos de pestaña, foco al navegar y "Saltar al contenido".
- `test_pantallas_pequenas.py`: sin desborde horizontal en 8 pantallas a 1440, 1024, 768, 390 y 320 px.
- `test_swagger_ui.py`: Swagger UI carga sin pedir nada a servicios externos y "Try it out" ejecuta una consulta real.
- Page Objects en `tests/support/pages/`: localizan por rol y nombre accesible y exponen localizadores para usarlos con `expect`. Las fixtures `consulta` y `resultado` están en `tests/conftest.py`.
- Datos en `tests/data/textos_interfaz.json` y `tests/data/pantallas.json`. La fixture `abrir_pantalla` deja la página en cualquier pantalla de esa lista.
- `base_url` y la ventana de 1440x900 están en `tests/conftest.py`. La fixture `aplicacion_levantada` detiene la corrida con instrucciones si falta un servidor. El navegador se elige con `--browser` y `--headed` (no hay variables `BROWSER` ni `HEADLESS`).
- Mutación verificada: cédula en la URL, quitar `DemoBanner`, conservar el estado al recargar, saltarse la validación del cliente, edad visible para el jurado, calles en todos los mapas, cédula sin puntos, nombre de la entidad real, salto que cambia la URL, sin foco al navegar, navegación sin `flex-wrap` (solo falla a 320 px) y contraste bajo (axe).
- axe no evalúa el contraste de los placeholders, y tampoco detectó una mutación de texto blanco sobre fondo blanco.

## Autenticación y roles

Funcionalidad nueva, aprobada por el usuario el 2026-11-18. El usuario ya había construido este producto antes: él decide cómo debe quedar y aprueba cada fase. **Pidió documentar muy bien cada fase.** Las decisiones importantes van en un ADR en `docs/decisiones/` (ver "Convenciones").

### Plan por fases (cada una en su rama y su pull request)

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Autenticación JWT y roles (backend) | ✅ en `main` desde el PR #9 (2026-11-18) |
| 2 | Modelo `RegistroConsulta`: una fila por consulta, **sin cédula** (fecha y hora, resultado, género, ciudad y edad del día). **Cambia `models.py`: necesita la aprobación del usuario** | ⏳ |
| 3 | API de administración: CRUD de las 6 entidades, asignar o quitar jurado, gestión de usuarios con las reglas del ADR 0001 | ⏳ |
| 4 | API del reporte: total, no encontradas y conteos por género, rango de edad y ciudad, con filtro por ciudad; para el Analista y el Administrador | ⏳ |
| 5 | Frontend: inicio de sesión, rutas protegidas, renovación del token y salir. Agrega el canal de interfaz de `inicio_sesion.feature` | ⏳ |
| 6a | Frontend: administración de datos y jurados (`/administracion`) | ⏳ |
| 6b | Frontend: gestión de usuarios | ⏳ |
| 7 | Frontend: reporte (`/reportes`) con tortas de género y edad, barras por ciudad, total destacado y filtro por ciudad | ⏳ |

### Decisiones aprobadas para las fases siguientes (2026-11-18)

- **Reporte:**
  - cuenta **todas** las consultas, también las repetidas;
  - rangos de edad 18–30, 31–50 y mayores de 50; los bordes 30, 31, 50 y 51 son casos de prueba;
  - tortas para el género y el rango de edad, barras para la ciudad, y el total destacado;
  - filtro por ciudad: con una ciudad elegida se oculta la gráfica por ciudad y las no encontradas no aparecen (avisarlo en pantalla).
- **Registro:** se cuentan también las consultas de **cédulas no encontradas**, que solo suman al total. No se registran el formato inválido ni el 429. La edad se guarda exacta y se agrupa en rangos al generar el reporte.
- **Diseño:** las pantallas nuevas no están en Figma. Claude las diseña con el estilo actual y muestra capturas para que el usuario las apruebe. Se podrán ajustar cuando vuelva el cupo del MCP de Figma.

### Fase 1: autenticación y roles (backend)

App nueva `apps/cuentas`: no tiene modelos propios y **no toca `models.py`**. ADR [0001](docs/decisiones/0001-roles-y-administracion-propia.md), [0002](docs/decisiones/0002-tokens-en-memoria-y-cookie-httponly.md) y [0003](docs/decisiones/0003-admin-de-django-solo-superusuario.md).

| Archivo | Contenido |
|---|---|
| `roles.py` | `ADMINISTRADOR`, `ANALISTA`, `ROLES` y `rol_de(usuario)`. Lee el rol de la base en cada llamada. Devuelve `None` si el usuario no existe, está inactivo, es superusuario o no tiene grupo de rol. Si está en los dos grupos, se le trata como administrador |
| `migrations/0001_grupos.py` | Migración de datos: crea los grupos `Administrador` y `Analista`. Los nombres se escriben literales, sin importarlos de `roles.py` |
| `permissions.py` | `TieneRol` (base), `TieneRolEnLaApp`, `EsAdministrador` y `EsAnalistaOAdministrador`. Las usarán las fases 3 y 4 |
| `services.py` | `iniciar_sesion`, `renovar_sesion` y `cerrar_sesion`, más la dataclass `Sesion` |
| `cookies.py` | Leer, poner y borrar la cookie del token de refresco |
| `excepciones.py` | `ErrorConCodigo` y sus subclases `DatosIncompletos`, `CredencialesInvalidas`, `SesionExpirada` y `SolicitudRechazada`, más las tuplas `DEMASIADOS_INTENTOS`, `USA_POST` y `USA_GET`, que comparten las vistas y `esquema.py` |
| `views.py`, `serializers.py`, `esquema.py`, `urls.py` | Los 4 endpoints y su documentación en Swagger (etiqueta "Sesión") |
| `throttles.py` | `IngresoRateThrottle` (tasa `ingreso`) |
| `sitio_admin.py` | `SitioAdminSoloSuperusuario` y `AdminSoloSuperusuarioConfig`, que reemplaza a `django.contrib.admin` en `INSTALLED_APPS`. No va en `apps.py` porque Django no admite dos configuraciones de app en el mismo `apps.py` (`RuntimeError: declares more than one default AppConfig`) |
| `management/commands/crear_usuarios_demo.py` | Crea o actualiza `admin.demo` y `analista.demo` con `DEMO_ADMIN_CONTRASENA` y `DEMO_ANALISTA_CONTRASENA`. Valida las dos contraseñas antes de tocar la base y nunca las muestra. Es idempotente: deja a los usuarios activos, sin `is_staff` ni superusuario y con un solo grupo |

**Endpoints** (`/api/auth/`, montado antes que `api/` en `config/urls.py`; es también la ruta de la cookie):

| Ruta | Detalle |
|---|---|
| `POST ingresar/` `{"usuario", "contrasena"}` | Sin autenticación, solo JSON y con el límite `ingreso`. Quita los espacios externos del usuario. Responde `{"acceso", "tipo": "Bearer", "expira_en": 900, "usuario": {"usuario", "nombre", "rol"}}` y pone la cookie |
| `POST refrescar/` | Sin cuerpo. Exige la cabecera `X-Requested-With: ConsultaVoto` y la cookie. Revoca el token anterior y entrega uno nuevo con el **mismo `exp`** |
| `POST salir/` | Exige la cabecera. Revoca el token si es válido y borra la cookie. Siempre responde 204 |
| `GET sesion/` | JWT, con `IsAuthenticated` y `TieneRolEnLaApp`. Devuelve `{"usuario", "nombre", "rol"}` |

**Errores nuevos** (todos con `{"codigo", "mensaje"}`):
- 400 `DATOS_INCOMPLETOS`;
- 401 `CREDENCIALES_INVALIDAS`: el mismo para un usuario inexistente, una contraseña incorrecta, un usuario desactivado, sin rol o superusuario;
- 401 `SESION_EXPIRADA`;
- 401 `NO_AUTENTICADO` y `TOKEN_INVALIDO`;
- 403 `SIN_PERMISO` y `SOLICITUD_RECHAZADA`;
- 405 `METODO_NO_PERMITIDO` con "Usa POST en esta ruta." o "Usa GET en esta ruta.";
- 429 `DEMASIADOS_INTENTOS`, con `Retry-After`.

Los mensajes están en `tests/data/mensajes_error.json`.

**Manejador central** (`apps/consultas/exceptions.py`). Elige el código en este orden:
1. el `codigo` propio de la excepción (`ErrorConCodigo`);
2. `errores_drf` de la vista, para textos propios por ruta;
3. `ERRORES_DRF`, que ahora incluye `NotAuthenticated`, `AuthenticationFailed` (y con ella `InvalidToken` de simplejwt) y `PermissionDenied`;
4. `ERROR_DE_SOLICITUD`.

El 405 de la consulta sigue diciendo "Usa POST para consultar.".

**Configuración** (`settings/base.py`):
- `DEFAULT_AUTHENTICATION_CLASSES = [JWTAuthentication]`. La consulta conserva `authentication_classes = []`: un token basura no la rompe, y hay una prueba de eso.
- **`SIMPLE_JWT`:** acceso de 15 minutos, refresco de 8 horas, HS256 con `SECRET_KEY` y `CHECK_USER_IS_ACTIVE`.
- **`JWT_COOKIE`:** nombre `consultavoto_refresco`, ruta `/api/auth/`, `SameSite=Strict` y `SECURE` según `env_bool('JWT_COOKIE_SECURE')`.
- **Otros:** `CABECERA_APP`, la tasa `ingreso` (`INGRESO_LIMITE_POR_MINUTO`, 5 por defecto) y la app `rest_framework_simplejwt.token_blacklist`.
- **`settings/test.py`:** fija `ingreso` en 5/min y `SECURE` en falso.

**Hallazgos durante la implementación:**
- **La rotación de simplejwt** (`TokenRefreshSerializer`) llama a `set_exp()`: con cada renovación la sesión se alargaría sin fin. Además hace `objects.get()` sobre el usuario, y si fue borrado da un 500. Por eso `renovar_sesion()` usa las piezas de simplejwt (`RefreshToken`, `blacklist`, `set_jti`, `set_iat` y `outstand`) sin `set_exp()`. Así la sesión dura como máximo 8 horas desde el inicio.
- **DRF revisa la autenticación antes que el método:** `POST /api/auth/sesion/` sin token da 401, no 405. Para probar el 405 hay que enviar un token válido.
- **Las cookies en el cliente de pruebas:** el cliente `api` de las pruebas black-box se comparte en toda la sesión de pytest, así que la cookie de una prueba pasaría a otra. Por eso existe la fixture `cliente_sesion` (`tests/support/sesion_client.py`), nueva en cada prueba.
- **Límites conocidos:**
  - el token de acceso sigue siendo válido hasta que vence (15 minutos como máximo) después de cerrar sesión;
  - `JWT_COOKIE_SECURE` debe ser `true` en cualquier despliegue con HTTPS.

**Pruebas de la fase 1:**
- **White-box, 92 nuevas (el backend pasa de 136 a 228), con 100 % de cobertura:**
  - `test_autenticacion.py` (56): cada atributo de la cookie, el token de refresco fuera del JSON, los 5 fallos de inicio de sesión con la misma respuesta, datos incompletos, 415 y 405, el límite de intentos y que `X-Forwarded-For` no lo evade, rotación, revocación, vencimiento conservado, usuario borrado, desactivado o sin rol al refrescar, la cabecera propia, cerrar sesión, tokens falsificados (vencido, firma alterada, otra clave, `alg: none` y token de refresco), el efecto inmediato y la consulta pública con un token basura;
  - `test_roles_y_permisos.py`;
  - `test_usuarios_demo.py`;
  - `test_manejador_errores.py`, ampliado.
- **Black-box:**
  - `tests/api/test_autenticacion.py` y 6 pruebas de documentación de la sesión en `test_documentacion_api.py`. La API pasa de 110 a 144;
  - `tests/bdd/features/inicio_sesion.feature`, con 7 escenarios por la API (la BDD por la API pasa de 14 a 21).
  - **Datos:** `tests/data/usuarios.json` (sin contraseñas: dice qué variable usar), `credenciales_invalidas.json` y `sesion.json`.
  - **Soporte:** `config.contrasena_demo()`, `openapi.EspecificacionOpenApi.de(ruta, metodo)` y `cabeceras_respuesta()`. El plugin de Allure adjunta también la última respuesta de `cliente_sesion` (`CLIENTES_API`).
- **Mutaciones:**
  - **12 en el backend, todas detectadas:** cookie sin `HttpOnly` o con `SameSite=Lax`, token de refresco en el JSON, mensaje distinto para un usuario inexistente, rotación sin revocar, rotación con `set_exp`, rol tomado del token, superusuario con acceso, `CHECK_USER_IS_ACTIVE` apagado, admin abierto a `is_staff`, sin límite de intentos y sin la cabecera.
  - **5 contra el servidor real, todas detectadas:** sin `HttpOnly`, rotación sin revocar, salir sin revocar, sin la cabecera y mensaje cambiado.
  - **Dos debilidades que encontraron las mutaciones y se corrigieron:**
    1. La primera versión de la prueba del vencimiento comparaba dos tokens creados en el mismo segundo y no notaba `set_exp()`. Ahora el token original vence en 1 hora.
    2. La primera mutación del "token en el JSON" no era un defecto real, porque el serializador descarta los campos que no declara.
- **Verificado en local (2026-11-18):** `python scripts/pruebas.py todo --allure --cobertura` pasó 228 + 165 + 128 pruebas (Chromium), con 100 % de cobertura, y devolvió 0. Se usaron contraseñas de demostración **temporales**, solo en el proceso de la corrida. Después el usuario agregó las suyas al `.env`, se corrió `base` y las 165 pruebas de API y BDD pasaron con ellas.
- **Base local:** `base` aplicó las migraciones `cuentas.0001_grupos` y `token_blacklist` (0001 a 0013) y creó `admin.demo` y `analista.demo`.
- **Verificado en el CI:**
  - PR #9 (corrida 44402017801): pasaron todos los trabajos;
  - sobre `main` (corrida 44402876424, commit `2f6a519`): pasaron todos, incluida la publicación;
  - el historial publicado registra la corrida con **777 pruebas** (577 → 605 → 605 → 644 → 777), y la cobertura publicada da **100 %** (627 líneas y 48 ramas, con `apps/cuentas`).

## Reporte de Allure

Un solo reporte de las cuatro suites. Se genera en local (README, paso 9) y en cada corrida del CI, como artefacto descargable (`reporte-allure`, unos 4 MB con los tres navegadores). El de `main` se publica en GitHub Pages (https://crisprog2.github.io/ClaudeProyectoRegistraduria/).
- **Historial (Allure 3):** `historyPath` en `allurerc.mjs` (variable `ALLURE_HISTORIAL` o, por defecto, `reportes/historial/history.jsonl`, fuera de Git) y `historyLimit: 30`. Cada generación agrega una línea JSON con los resultados de la corrida. Las tendencias están en **Report ▾ → Gráficas** (por ejemplo, "Status dynamics"), y cada prueba muestra su propio historial. Verificado en local: sin archivo previo se genera bien, y tras tres generaciones el gráfico mostró tres corridas, también servido desde una subcarpeta como la de Pages.
- El único 404 del reporte es `widgets/metrics.json`, un widget opcional que no está configurado; no afecta.
- En Windows, `npm run generar` falló una vez con `EPERM ... rename allure-report/awesome/data`: un bloqueo momentáneo de archivos, probablemente del antivirus. Repetirlo funciona.
- **Por qué Allure 3:** funciona con Node y no exige Java, que no está instalado. Va en `reportes/`, con su propio `package.json` y su lock (`allure` 3.33.0), separado del frontend. Configuración en `reportes/allurerc.mjs`: idioma español, agrupación por `parentSuite`/`suite`/`subSuite` y etiquetas `host` y `thread` ocultas, porque muestran el nombre del equipo.
- **Solo `allure-pytest` (2.16.2), en los dos `requirements.txt`:** no se usa `allure-pytest-bdd` porque los dos registran `--alluredir` y pytest no arranca si están instalados juntos. Eso rompería también el backend, que comparte el `.venv`. Los pasos de Gherkin se registran con los hooks de pytest-bdd.
- **Plugin `tests/support/allure_reporte.py`**, registrado con `pytest_plugins` en `tests/conftest.py`:
  - **Agrupación:** asigna el nivel (API, BDD, E2E). En BDD agrega el canal ("Por la API" o "Por la interfaz") y el feature, porque los mismos escenarios corren dos veces.
    - **Cómo lo deduce, con índices negativos de Python (`-1` = último elemento):** `_carpetas()` toma la ruta del archivo de prueba relativa a la raíz y usa `.parts[:-1]`, que quita el nombre del archivo y deja solo las carpetas. Por ejemplo, `tests/bdd/step_defs/interfaz/test_consulta_jurado.py` queda como `('tests', 'bdd', 'step_defs', 'interfaz')`. El nivel es `carpetas[1]` (`api`, `bdd` o `e2e`), y en BDD el canal es `carpetas[-1]`, la última carpeta (`api` o `interfaz`), que `CANALES_BDD` traduce a "Por la API" o "Por la interfaz".
    - **Revisado el 2026-11-12, a pedido del usuario:** no es un error. `carpetas[-1]` solo se usa cuando el nivel es `bdd`, así que siempre hay al menos dos carpetas y no puede fallar por índice. Comprobado con las rutas reales de API, BDD por la API, BDD por la interfaz y E2E, y en el reporte publicado. Se decidió no cambiar el código.
    - **Límite conocido (solo cosmético):** si una prueba se pusiera directamente en `tests/bdd/`, sin `step_defs/api` ni `step_defs/interfaz`, `carpetas[-1]` sería `bdd` y el reporte mostraría el grupo "bdd" en lugar de un canal. No rompe nada, y la convención del proyecto separa los steps por canal. Una carpeta de canal nueva aparecería con su propio nombre hasta agregarla a `CANALES_BDD`.
  - **Escenarios BDD:** título, descripción tomada de la historia de usuario del feature (sin ella, Allure muestra la ruta del archivo en el disco), pasos de Gherkin y cada columna del ejemplo como parámetro.
  - **Severidad:** las `smoke` son críticas.
  - **Evidencia en fallos:** la petición y la respuesta de la API (`ConsultaApiClient.ultima_respuesta`, que se reinicia antes de cada prueba porque el cliente dura toda la sesión), y la URL, la captura y la traza de Playwright. La traza se toma del registro de artefactos de pytest-playwright (atributo privado `_playwright_artifacts_recorder`): si se actualiza pytest-playwright, revisarlo.
  - **Entorno:** escribe `environment.properties` con versiones y URLs, sin secretos. No incluye los navegadores: en el CI cada trabajo escribe el suyo y al juntarlos solo quedaba el último.
- **Backend:** `backend/tests/conftest.py` solo asigna el grupo "Backend"; el backend no importa nada de `tests/support/`.
- **`reportes/preparar-resultados.mjs`** se ejecuta antes de generar: quita las fixtures que terminaron bien (unas 13 000 por corrida) y el parámetro interno `_pytest_bdd_example`, porque Allure 3 no respeta el modo oculto.
- **`--alluredir=` siempre con signo igual:** con un espacio y la carpeta ya creada, pytest toma la ruta como argumento, cambia el `rootdir` y el backend pierde su `pytest.ini`.
- **Visor:** `allure open` escucha por defecto en todas las interfaces de red; el script lo limita a `127.0.0.1`.
- **Verificado:** con dos pruebas temporales que fallaban a propósito, se adjuntaron la petición y la respuesta 404 en la de API, y la URL, la captura y la traza en la de interfaz. Se borraron después.
- **Fuera de Git:** `reportes/allure-results/` y `reportes/allure-report/`. Se retiró `pytest-html`, que no se usaba.

## Cobertura de código

Solo del backend, medida con las pruebas white-box (fase 1). `pytest-cov` 7.1.0 y `coverage` 7.17.3, fijadas en `backend/requirements.txt` (coverage también, para que el porcentaje no cambie con otra versión).
- **Configuración en `backend/.coveragerc`:** mide `apps` y `config` con ramas (`branch = True`). Excluye las migraciones, `settings/local.py`, `asgi.py` y `wsgi.py`, cada una con su motivo en un comentario. `fail_under = 95`.
- **Solo con `scripts/pruebas.py backend --cobertura`** (o `todo --cobertura`), no en `pytest.ini`: con `addopts`, correr una sola prueba fallaría por cobertura baja.
- **Salidas en `reportes/cobertura/`** (fuera de Git): HTML (`index.html`) y `coverage.xml`, más la tabla en la terminal. En el CI, `resumen_cobertura_en_github()` agrega la tabla en Markdown a `GITHUB_STEP_SUMMARY`; en local esa variable no existe y no hace nada.
- **En el CI:** dentro del trabajo `Backend (white-box)`, así que no hay un check nuevo ni que tocar el ruleset. El artefacto `cobertura-backend` se guarda aunque falle (`if: !cancelled()`). El trabajo `reporte` lo descarga en `allure-report/cobertura/` después de generar el reporte de Allure, porque la generación reescribe esa carpeta, y con `continue-on-error`, para que el reporte de Allure se publique aunque falte la cobertura. Así el artefacto `reporte-allure` y GitHub Pages la incluyen: https://crisprog2.github.io/ClaudeProyectoRegistraduria/cobertura/.
- **El mínimo:** el 95 % lo aprobó el usuario el 2026-11-17. Deja margen para cambios pequeños y detecta un módulo nuevo sin pruebas. Cambiarlo solo de forma consciente y explicándolo en el pull request.
- **Medición inicial (2026-11-17):** 92 % con las 97 pruebas de entonces. Faltaban el admin (81 %: ninguna prueba lo abría), los `__str__` y la propiedad `edad` (90 %), los errores de configuración de `env_requerida` y `env_entero_positivo`, y el caso de error no controlado del manejador de errores. Lo crítico (validadores, servicios, serializadores y vista) ya estaba al 100 %.
- **Pruebas agregadas (39, el backend pasa de 97 a 136), 100 % de líneas y ramas:**
  - `test_admin.py`: los 6 listados y la ficha de una persona abren con `admin_client` (superusuario que pytest-django crea solo en la base de pruebas); el filtro "es jurado" con sí, no y sin filtro; las columnas "es jurado" y "vota en la misma mesa"; y que el listado de personas no haga una consulta por fila.
  - `test_models.py`: los `__str__` documentados y `edad`.
  - `test_configuracion.py`: variable obligatoria ausente o vacía, y entero positivo válido, vacío e inválido (`0`, `00`, `-5`, `1.5`, `abc`, `10/min`).
  - `test_manejador_errores.py`: error no controlado (devuelve `None` y Django responde 500), un error de DRF sin código propio (el 401 de `NotAuthenticated` sale como `ERROR_DE_SOLICITUD`, útil para cuando llegue JWT) y el 404 de Django, que conserva el formato.
- **Hallazgo con el conteo de consultas:** con `list_select_related` el listado de personas hace 6 consultas; sin él, 16 (una por persona, por la columna "Es jurado"). En `Mesa` y `DesignacionJurado` quitarlo no cambia nada: Django aplica `select_related` por su cuenta a las `ForeignKey` de `list_display`. Solo la designación, que es una relación inversa, depende de `list_select_related`; por eso la prueba es solo de `Persona`, con un límite de 8.
- **Mutación verificada:** un módulo nuevo sin pruebas baja la cobertura a 92,2 % y el comando termina con código 1, aunque las 136 pruebas pasen. También se detectan: el filtro "es jurado" invertido, la mesa sin ceros a la izquierda en `__str__`, aceptar `0` como límite de consultas y quitar `list_select_related` de `PersonaAdmin`.
- **Observación sin cambiar (models.py es del usuario):** la propiedad `Persona.edad` usa `date.today()`, la fecha del sistema, mientras que la API usa `timezone.localdate()`, la de America/Bogota. Solo la usa el admin. Si el servidor estuviera en otra zona horaria, cerca de la medianoche el admin podría mostrar una edad distinta de la API el día del cumpleaños.
- **Fases siguientes (opcionales):** 2) medir el backend mientras corren las pruebas black-box: exige apagar `runserver` de forma ordenada, porque `coverage` solo guarda los datos al salir y hoy `scripts/pruebas.py` lo cierra a la fuerza en Windows; 3) frontend: Playwright para Python no expone la cobertura del navegador, habría que instrumentar con `vite-plugin-istanbul`.

## Integración continua

`.github/workflows/ci.yml` (GitHub Actions) corre en cada pull request y push a `main`, y a mano (`workflow_dispatch`).
- **Trabajos:** `backend` (con `--cobertura`: falla si baja del 95 % y guarda el artefacto `cobertura-backend`), `api` (API y BDD por la API), `frontend` (`npm run build`), `interfaz` (matriz chromium/firefox/webkit, `fail-fast: false`) y `reporte`. Este último junta los `allure-results-*` con `download-artifact` (`merge-multiple`), genera el reporte con `reportes/` y lo publica como artefacto `reporte-allure`, aunque haya fallas (`if: !cancelled()`). También incluye el reporte de cobertura en `allure-report/cobertura/`. En los push a `main`, además, descarga el historial publicado, lo incluye en el sitio y prepara el artefacto de Pages. El trabajo `publicar` lo despliega.
- **Lógica en `scripts/pruebas.py`, no en el YAML:** comandos `base`, `backend`, `api`, `interfaz` y `todo`, con `--allure`, `--limpiar-allure`, `--cobertura` (solo `backend` y `todo`) y `--browser` (repetible). Levanta los servidores que necesita, espera a que respondan, los apaga siempre (en Windows cierra el árbol de procesos de npm con `taskkill /T`) y devuelve el código de pytest. Se detiene si el puerto ya está ocupado. Solo usa la biblioteca estándar y python-dotenv. Así, un futuro Jenkinsfile o el uso local llaman a lo mismo.
- **`base` no corre solo:** carga `datos_demo` y sobrescribe esos registros, y además aplica las migraciones y crea los usuarios de demostración (`crear_usuarios_demo`), así que en local se llama a mano. En CI cada trabajo lo llama sobre un contenedor nuevo.
- **MySQL:** servicio `mysql:8.0` por trabajo, definido una vez con un ancla YAML (`&mysql` / `*mysql`; GitHub admite anclas desde 2025-09, pero no claves de combinación). Las claves están escritas en el YAML porque solo valen en ese contenedor temporal. `services` no puede leer el contexto `env`, así que ahí van literales.
- **`.github/actions/preparar-entorno`** (acción compuesta): instala Python con caché de pip, genera `DJANGO_SECRET_KEY` (enmascarada) y da permisos sobre `test_registraduria` conectándose como root con PyMySQL. Sin ese permiso, pytest-django no podría crear la base de pruebas.
- **Configuración:** Python 3.11, Node 26, `DJANGO_DEBUG=true` (Swagger necesita sus estáticos), `DEMO_ADMIN_CONTRASENA` y `DEMO_ANALISTA_CONTRASENA` (valores solo para el CI, como las claves de MySQL) y `JWT_COOKIE_SECURE=false`. El script fija `CONSULTA_LIMITE_POR_MINUTO=1000` e `INGRESO_LIMITE_POR_MINUTO=1000` para el backend que levanta.
- **Seguridad:** `permissions: contents: read`, acciones fijadas por versión exacta (`checkout` v7.0.1, `setup-python` v7.1.0, `setup-node` v7.1.0, `upload-artifact` v7.0.2, `download-artifact` v8.0.2), `concurrency` cancela la corrida anterior solo en las ramas de pull request (`cancel-in-progress` es falso en `main`, para no cortar una publicación ni perder un punto del historial).
- **Máquinas fijadas en `ubuntu-24.04`**, no `ubuntu-latest`: en la primera corrida (2026-11-11, PR de `feature/pipeline-ci`) `ubuntu-latest` ya era Ubuntu 26.04 ("resolute") y `playwright install --with-deps` falló con "Temporary failure resolving 'archive.ubuntu.com'" tras unos 11 minutos. Firefox y WebKit se cortaron a los 30 minutos. pip y npm sí descargaron. Fijar la versión además evita que el CI cambie de sistema sin aviso. En la segunda corrida, ya en 24.04 y con 3 reintentos, falló igual ("Temporary failure resolving 'azure.archive.ubuntu.com'") y se cortó a los 30 minutos, con GitHub reportando todo operativo. Conclusión: las máquinas no resuelven los servidores de paquetes de Ubuntu, sea cual sea la versión.
- **Trabajos de interfaz dentro de `mcr.microsoft.com/playwright/python:v1.64.1-noble`** (imagen oficial de Playwright, misma versión que `tests/requirements.txt`): trae los navegadores y sus librerías, así que no usan `apt`. Opciones `--ipc=host` (recomendado para Chromium). Dentro del contenedor MySQL se alcanza como `mysql` (`MYSQL_HOST: mysql` en ese trabajo). Si se actualiza Playwright, hay que actualizar también la etiqueta de la imagen.
- **Sin caché de pip en los trabajos de interfaz** (`preparar-entorno` con `cache-pip: ''`): en la tercera corrida `setup-python` instaló 3.11 en el contenedor, pero su caché ejecuta el script `pip`, cuya primera línea apunta a `/opt/hostedtoolcache`, que dentro del contenedor está montado en `/__t` ("spawn .../pip ENOENT"). Las dependencias se instalan con `python -m pip`, que no depende de ese script. Si esto fallara, la alternativa es usar el Python de la imagen.
- **`HOME: /root` en los trabajos de interfaz:** en la cuarta corrida pasaron Chromium y WebKit, pero Firefox no arrancó ("Firefox is unable to launch if the $HOME folder isn't owned by the current user"). GitHub pone `HOME=/github/home`, de otro usuario, y el contenedor corre como root. Es la solución que indica el propio mensaje de Playwright.
- **Permisos de la base de pruebas con PyMySQL**, no con `docker exec`: dentro de un contenedor no existe `docker`. La acción `preparar-entorno` lee la conexión de las variables `MYSQL_*` y sirve en los dos casos.
- **Puesta en marcha (2026-11-11, cinco corridas):** 1) Ubuntu 26.04: la interfaz no pudo instalar navegadores con `apt`. 2) Ubuntu 24.04: igual. 3) Imagen de Playwright: falló la caché de pip. 4) Sin caché: pasaron Chromium y WebKit, y Firefox no arrancó por `HOME`. 5) Con `HOME: /root`: los siete trabajos pasaron (https://github.com/crisprog2/ClaudeProyectoRegistraduria/actions/runs/43059436476). En todas, backend, API y frontend pasaron, y el trabajo `reporte` publicó `reporte-allure` aunque hubiera fallas.
- **Confirmado en la corrida exitosa:** PyMySQL funciona con el contenedor de MySQL sin `cryptography`, en la máquina y dentro del contenedor de Playwright. Las pruebas de pantallas pequeñas pasan con las fuentes de Linux. `test_saltar_al_contenido_mueve_el_foco_sin_perder_el_resultado[webkit]` también pasó. Tiempos: backend 56 s, API 59 s, frontend 11 s, Chromium 3 min 12 s, Firefox 4 min 7 s, WebKit 3 min 2 s, reporte 21 s; unos 5 minutos en total, porque corren en paralelo.
- **Protección de `main`** (ruleset "Proteger main", activo desde 2026-11-11; lo creó el usuario en GitHub): exige pull request con 0 aprobaciones (trabaja solo y GitHub no deja aprobar un PR propio), los 6 checks de pruebas (`Backend (white-box)`, `API y BDD por la API`, `Frontend (build)`, `Interfaz (chromium)`, `Interfaz (firefox)` e `Interfaz (webkit)`), rama al día con `main`, y prohíbe borrar `main` y el force push. "Reporte de Allure" no es obligatorio porque pasa aunque fallen las pruebas. Si se renombra un trabajo del workflow, hay que actualizar el ruleset, o el PR quedará esperando un check que ya no existe. La API pública no muestra la lista de excepciones (bypass). La regla de PR trae `require_extra_approval_for_unattributed_changes` activo por defecto: si un PR se bloquea pidiendo aprobación con el CI en verde, revisar eso primero. Se verifica sin autenticación con `GET /repos/crisprog2/ClaudeProyectoRegistraduria/rules/branches/main`.
- **GitHub Pages:** el trabajo `publicar` corre solo en push a `main`, después de `reporte` y aunque alguna suite falle, porque el historial debe registrar las fallas (`if: !cancelled() && needs.reporte.result == 'success' && push a main`). Usa `actions/upload-pages-artifact` v5.0.0 (en `reporte`) y `actions/deploy-pages` v5.0.1, con permisos `pages: write` e `id-token: write` solo en ese trabajo y el entorno `github-pages`. Pages se activó en Settings → Pages → Source: GitHub Actions; lo hace el usuario. No usa `configure-pages`, para no darle permisos de Pages al trabajo `reporte`.
- **Historial en el propio sitio:** `URL_PAGES` (`https://<dueño>.github.io/<repo>`) se arma con el contexto `github`. En `main`, el trabajo `reporte` descarga `$URL_PAGES/historial/history.jsonl` con `curl -f` (si responde 404 o falla, sigue sin historial y deja un aviso), genera el reporte y copia el historial actualizado a `allure-report/historial/`. Así no hacen falta una rama `gh-pages` ni acciones de terceros. Los pull requests no descargan ni publican el historial.
- **Lo que queda público:** nombres de pruebas, resultados, versiones, URLs locales del entorno y, en los fallos, capturas y trazas de Playwright. Todo con datos ficticios y sin secretos. El usuario aprobó publicarlo.
- **Verificado en local (Windows):** `python scripts/pruebas.py todo --allure` corrió 97 + 124 + 128 pruebas en Chromium, devolvió 0 y apagó los dos servidores. Con el puerto 8000 ocupado se detiene sin correr pruebas; con una prueba que falla devuelve 1 y apaga el servidor. El YAML se validó con PyYAML; el flujo completo solo se puede probar en GitHub.

## Frontend

Se construye por fases y cada una se revisa con capturas de Playwright a 1440 px comparadas con el Figma: 1) base y layout, 2) consulta, 3) resultado, 4) accesibilidad, ajuste a pantallas pequeñas, 404 y documentación.

Decisiones:
- **Conexión con la API**: en desarrollo Vite reenvía `/api` al backend (`API_BASE_URL`, por defecto `http://127.0.0.1:8000`). El navegador ve un solo origen y no depende de CORS. `vite.config.js` lee el `.env` de la raíz (`envDir: '..'`); solo las variables `VITE_*` llegan al navegador.
- **Flujo de datos**: `ConsultaPage` llama a la API y, si sale bien, navega a `/consulta/resultado` con el resultado en el estado de navegación. Si alguien recarga o entra directo al resultado, vuelve a `/consulta`.
- **Validación en el navegador**: las mismas reglas del backend (6 a 10 dígitos, sin 0 inicial). El backend sigue siendo la regla definitiva.
- **Selectores para pruebas**: HTML semántico y accesible (`label`, roles, `aria-current`, `aria-invalid`, `aria-live`). `data-testid` solo si no hay alternativa.
- **Estilos**: CSS Modules (`Componente.module.css`) y variables de `styles/tokens.css`; no hay valores de color sueltos en los componentes. `global.css` define `.contenedor` (1200 px centrados, que a 1440 px dejan los 120 px de margen del Figma) y `.solo-lector`.
- **Fuente**: Inter instalada en el proyecto (`@fontsource-variable/inter`), sin peticiones a Google Fonts.
- **Íconos**: SVG descargados del Figma en `src/assets/iconos/`, con nombres en español.
- **Mapa**: ilustración estática con el aviso "ILUSTRATIVO", sin servicios de mapas externos.
- **Errores no diseñados en el Figma** (429 y servidor caído): reutilizan el panel de `ConsultaSinResultado` con su propio texto ("Hiciste demasiadas consultas" / "No pudimos completar la consulta").
- **Estados de la consulta**: debajo del campo se muestra solo una cosa, en lugar de la ayuda: `FormError` (vacío o formato; borde rojo de 2 px, `aria-invalid`, foco al campo) o `ConsultaSinResultado` (no encontrada, 429, sin conexión; borde normal). Ambos con `role="alert"`. Al editar el campo el error desaparece. El campo tiene placeholder "Ej.: 1023456789".
- **Colores de error** (de los frames de error del Figma): borde `#c9454c`, texto `#b3363d`, panel `#fbeeef` con borde `#f0c9cc`.
- **Recarga**: el navegador conserva `history.state` al recargar, así que `main.jsx` lo borra al cargar la página. Sin esto, el resultado sobreviviría a la recarga.
- **Textos del jurado** (`utils/textosJurado.js`): "misma mesa" es el texto del Figma; "otra mesa" y "otro puesto" no están en el Figma y los aprobó el usuario.
- **Mapa de un jurado**: siempre muestra el lugar de votación; si sirve en otro puesto, la nota azul lo nombra. Los nombres de calles solo se muestran en `Calle 48 # 65-20` (Medellín), porque el dibujo corresponde a ese puesto; los demás usan el mismo plano sin nombres.
- **Ciudad y departamento iguales** (Bogotá, D.C.): el mapa muestra el nombre una vez (`formatearLugar`); los campos de la tarjeta muestran ambos.
- **Pantallas pequeñas**: el Figma solo diseña 1440 px, así que este comportamiento es criterio propio. A 1100 px o menos las columnas se apilan; a 768 px el header y los pasos se reorganizan; a 600 y 480 px se reducen títulos y rellenos. Sin desborde horizontal de 1440 a 320 px. El plano del mapa tiene manzanas adicionales que solo se ven a todo el ancho, y la brújula está anclada a la derecha.
- **Accesibilidad**: enlace "Saltar al contenido" (mueve el foco a mano, porque un cambio de hash borraría el estado de navegación), título de pestaña por pantalla (`useTituloPagina`) y foco en el `h1` al cambiar de pantalla (`PageHeading enfocar`). Auditado con axe-core en cada corrida de `tests/e2e/test_accesibilidad.py`: 0 violaciones en las 8 pantallas.
- **Placeholder**: `#66778b` (4.59:1) en lugar del `#8a9bb0` del Figma (2.84:1), que no cumple WCAG AA. axe no evalúa el contraste de los placeholders.
- **Página 404**: no está en el Figma; reutiliza el layout, `PageHeading` y `Card`.
- **Versiones exactas** en `package.json` (sin `^`) y `package-lock.json` versionado.
- Las constantes de las rutas viven en `utils/rutas.js` para evitar una importación circular entre `routes.jsx` y las páginas.
- "Cómo consultar" y "Ayuda" son `<a aria-disabled="true">` sin `href`: se ven como enlaces, pero no se pueden enfocar ni navegar.

## Convenciones

- **Idioma**: dominio, nombres de archivos, componentes, tests y features en español (`ConsultaPage`, `test_validaciones_cedula.py`). Términos técnicos estándar en inglés (`conftest`, `services`, `hooks`).
- **Backend**: lógica en `services.py`, reglas de formato en `validators.py`; las vistas se mantienen delgadas.
- **Frontend**: `pages/` = una por pantalla; `components/` agrupado por `layout/`, `common/`, `consulta/` y `resultado/`. Llamadas HTTP solo desde `services/api.js`. Colores y tipografía en `styles/tokens.css`.
- **Pruebas**:
  - Page Object Model en `tests/support/pages/`, compartido por E2E y BDD. Los tests no usan selectores directamente.
  - Un `conftest.py` por nivel (`tests/`, `tests/api/`, `tests/bdd/`, `tests/e2e/`, `backend/tests/`).
  - Datos de prueba en `tests/data/*.json`; nada de datos quemados en los tests.
  - BDD: `features/` separado de `step_defs/api/` y `step_defs/interfaz/`; los steps reutilizables de cada canal van en su `common_steps.py`.
  - Markers declarados en `pytest.ini` (`api`, `bdd`, `e2e`, `smoke`); `--strict-markers` activo. `regression` se retiró: correr todo sin filtros es la regresión completa.
  - Los pasos para correr las suites van en `scripts/pruebas.py`, no en el YAML del CI, para que local, GitHub Actions y un futuro Jenkins usen la misma lógica.
  - Reporte de Allure: un nivel nuevo de pruebas necesita su grupo (`parent_suite`) en `tests/support/allure_reporte.py` o en su `conftest.py`, y `--alluredir=` siempre va con signo igual. Los plugins de pytest propios viven en `tests/support/` y se registran con `pytest_plugins` en `tests/conftest.py`.
  - Escenarios mínimos a cubrir: solo votante, jurado en la misma mesa, jurado en otra mesa o puesto, campo vacío, formato inválido y cédula no encontrada.
- **Ramas y pull requests**: todo cambio, incluida la documentación, va en una rama (`feature/...`, `fix/...`, `docs/...`) con pull request hacia `main`, porque `main` está protegida y no admite push directo. El merge solo es posible con el CI en verde; lo hace el usuario en GitHub.
- **Configuración**: todo por variables de entorno (ver `.env.example`); nunca subir `.env`.
- **Documentación del código**: docstring en cada módulo, clase y función pública, en español. En el frontend: comentario inicial en cada archivo JS y CSS, y JSDoc en cada componente y función. Los `__str__` llevan un ejemplo del texto que producen. Las clases `Meta` no necesitan docstring. En pruebas, el nombre `test_*` describe el caso; el docstring solo se agrega cuando la intención no es obvia.
- **Pruebas que importan**: cuando una prueba protege una regla de seguridad o de negocio, comprobar al menos una vez que falla si se reintroduce el defecto (prueba de mutación), no solo que pasa.
- **Cobertura**: el código nuevo del backend llega con sus pruebas; si la cobertura baja del 95 %, el CI no deja fusionar. Excluir un archivo de la medición o bajar el mínimo solo con un motivo escrito en `backend/.coveragerc` y en el pull request.
- **Decisiones de arquitectura (ADR)**: cada decisión importante va en `docs/decisiones/NNNN-titulo.md`, con estado, fecha, aprobación, contexto, opciones, decisión, consecuencias y "Cómo se verifica". Hay que agregarla a la tabla cronológica de `docs/decisiones/README.md`. Un ADR no se borra: si la decisión cambia, otro lo reemplaza.
  - El número es el orden en que se escribió, no la fecha de la decisión. 0001 a 0003 son de la fase 1 de roles. 0004 a 0022 son **retroactivos**: el 2026-11-18, a pedido del usuario, se documentaron todas las decisiones desde el inicio del proyecto, con `CLAUDE.md`, el README y el historial de Git, y cada uno cita sus commits. **El siguiente libre es 0023.**
  - Si una sección de este archivo cambia una decisión que tiene ADR, hay que actualizar también el ADR, o reemplazarlo con uno nuevo.
- **Fases de roles y acceso**: antes de cada fase, mostrar el detalle y esperar la aprobación del usuario. Al terminarla, documentarla a fondo (README, `CLAUDE.md` y sus ADR).
- **Al terminar una tarea**: actualizar la sección "Estado" de este archivo y, si cambia algo visible para quien usa el repo, el README (tabla "Estado del proyecto" y "Ejecución").

## Estado

- ✅ Estructura base del monorepo.
- ✅ Modelo de datos definido y revisado (validado con system checks y pruebas en SQLite en memoria).
- ✅ Entorno virtual `.venv/` con dependencias fijadas y navegadores de Playwright.
- ✅ Settings de Django (`base` / `local` / `test`) leyendo del `.env` de la raíz. `manage.py` usa `local` por defecto y `backend/pytest.ini` usa `test`.
- ✅ Base local `registraduria` (utf8mb4_0900_ai_ci, modo estricto) con usuario `consultavoto_app`, que solo tiene permisos sobre `registraduria` y `test_registraduria`. Migración `0001_initial` aplicada.
- ✅ Fixture `backend/apps/consultas/fixtures/datos_demo.json` cargado en `registraduria` (`python manage.py loaddata datos_demo`).
- ✅ Admin de Django configurado para los 6 modelos; `__str__` legibles en `Mesa` y `DesignacionJurado`.
- ✅ Código del backend documentado con docstrings; README con instrucciones de ejecución del backend.
- ✅ Superusuario local creado por el usuario (no compartir ni registrar su contraseña).
- ✅ Figma actualizado: marca ConsultaVoto en las 3 pantallas, aviso neutro del votante y 3 pantallas de estados de error. Fixture alineado con el Figma (cédula `1023456789`).
- ✅ API REST de consulta (`POST /api/consulta/`) con manejador central de errores y límite de consultas por IP.
- ✅ Pruebas white-box del backend: 97 pasan contra MySQL; mutación de `NUM_PROXIES` detectada. Con la cobertura (2026-11-17) son 136, y con la fase 1 de roles, 228.
- ✅ Límite de consultas configurable con `CONSULTA_LIMITE_POR_MINUTO`.
- ✅ Pruebas black-box de la API: 110 pasan contra `runserver`; datos en `tests/data/`; mutaciones detectadas.
- ✅ Pruebas BDD (pytest-bdd, Gherkin en español): 14 casos pasan contra la API; mutaciones detectadas.
- ✅ Frontend fase 1: dependencias con versiones exactas, Vite con proxy, router, tokens y layout común (TopBar, SiteHeader, MainNav, FlagStripe, DemoBanner, Breadcrumb, Stepper, PageHeading, SiteFooter). Capturas comparadas con el Figma.
- ✅ Frontend fase 2: pantalla de consulta completa (`CedulaForm`, `PromoPanel`, `PasosConsulta`), validación en el cliente, `services/api.js`, hook `useConsultaCedula` y los 3 estados de error del Figma, más 429 y servidor caído. Verificado con Playwright: los errores del campo no llaman a la API, el foco vuelve al campo y la consulta exitosa navega sin la cédula en la URL.
- ✅ Frontend fase 3: pantalla de resultado para votante y jurado (misma mesa, otra mesa y otro puesto). Verificado con Playwright en los 10 ciudadanos del fixture; recarga y entrada directa vuelven a `/consulta`. El usuario la validó manualmente con el backend y el frontend corriendo. Después se cubrió con pruebas automatizadas de interfaz (ver "Pruebas de interfaz").
- ✅ Frontend fase 4: accesibilidad (0 violaciones de axe), ajuste a pantallas pequeñas de 1440 a 320 px y página 404.
- ✅ Pruebas de interfaz: 14 casos BDD y 112 E2E pasan en Chromium, Firefox y WebKit; mutaciones detectadas. Los 2 E2E de Swagger UI también pasan en los tres navegadores.
- ✅ Todo el código documentado (backend, pruebas y frontend).
- ✅ Controlador de MySQL cambiado a PyMySQL, ya en `main` (commit `8694003`): Windows bloqueó mysqlclient el 2026-11-09. Explicado en el README (paso 1, "Controlador de MySQL").
- ✅ Swagger UI y OpenAPI 3.1, en `main` desde el PR #1 (2026-11-06). `env_bool` ya usa el valor por defecto cuando la variable está vacía (antes, un `DJANGO_DEBUG=` vacío apagaba `DEBUG` y dejaba sin estilos al admin).
- ⚠️ El Control inteligente de aplicaciones de Windows 11 está activo en el equipo del usuario. El 2026-11-09 bloqueó una vez archivos de WebKit (`JavaScriptCore.dll`, `sqlite3.dll`), y las 114 pruebas E2E de WebKit fallaron al arrancar; en las corridas siguientes no se repitió. Si WebKit falla en bloque, revisar primero los eventos 3077 del registro *Microsoft-Windows-CodeIntegrity/Operational* (comando en el README). No desactivar esa protección sin que el usuario lo decida.
- ⚠️ Prueba posiblemente inestable: `test_saltar_al_contenido_mueve_el_foco_sin_perder_el_resultado[webkit]` falló una vez dentro de la suite completa en Windows (un elemento no quedó dentro de la ventana visible). Después pasó 5 de 5 veces sola, en la corrida completa siguiente y en el CI (Linux). Investigar si se repite.
- ✅ Reporte de Allure local con las cuatro suites (349 pruebas), en `main` desde el PR #2 (2026-11-11).
- ✅ Pipeline de CI en GitHub Actions y `scripts/pruebas.py`, en `main` desde el PR #3 (2026-11-11): 605 pruebas por corrida, con el reporte de Allure como artefacto. La primera corrida sobre `main` pasó (https://github.com/crisprog2/ClaudeProyectoRegistraduria/actions/runs/43062173386). Badge de CI en el README.
- ✅ `main` protegida con el ruleset "Proteger main": exige PR y el CI en verde (ver "Integración continua").
- ✅ Reporte de Allure en GitHub Pages con historial, en `main` desde el PR #5 (2026-11-12): publicado en https://crisprog2.github.io/ClaudeProyectoRegistraduria/, con el primer despliegue verificado.
- ✅ Escenarios BDD de interfaz separados por navegador, en `main` desde el PR #6 (2026-11-12). Ver "Caso resuelto" en la sección de pruebas BDD. Verificado en el reporte publicado: 605 pruebas (antes 577) y ninguna repetida. El historial de Pages registra las dos corridas (577 → 605).
- ✅ Cobertura de código del backend, en `main` desde el PR #8 (2026-11-17): 100 % de líneas y ramas, con un mínimo del 95 % en el CI. Confirmado en la corrida sobre `main`: 644 pruebas y el reporte publicado en https://crisprog2.github.io/ClaudeProyectoRegistraduria/cobertura/ (342 líneas y 24 ramas, 100 %).
- ✅ Roles y acceso, fase 1 de 8, en `main` desde el PR #9 (2026-11-18):
  - JWT, roles, `/admin/` solo para el superusuario y usuarios de demostración;
  - 22 ADR (3 de la fase y 19 retroactivos, desde el inicio del proyecto);
  - 17 mutaciones detectadas;
  - confirmado en la corrida sobre `main`: 777 pruebas y 100 % de cobertura (ver "Fase 1" en "Autenticación y roles");
  - el usuario tiene `DEMO_ADMIN_CONTRASENA` y `DEMO_ANALISTA_CONTRASENA` en su `.env`.
- ⏳ Siguiente: fase 2 (registro de consultas, con un cambio en `models.py` que el usuario debe aprobar). Ver el plan en "Autenticación y roles". Jenkins es opcional y reutilizaría `scripts/pruebas.py`.
- ⚠️ El MCP de Figma (plan Starter) agotó su límite de llamadas el 2026-11-03. El frame del jurado (`6:2609`) se implementó desde una captura del usuario: textos y estructura son exactos, y algunas medidas y colores son aproximados (`--color-borde-azul`, tamaño de `018 · Jurado`). Conviene compararlo con el Figma cuando haya cupo.

## Datos de demostración (`datos_demo.json`)

- **Geografía real (pública):** los 33 departamentos con código DIVIPOLA del DANE, sus capitales y algunos municipios extra (39 ciudades).
- **Todo lo demás es ficticio:** puestos (código = municipio 5 + zona 2 + puesto 2), mesas, personas y designaciones. Las cédulas siguen el formato colombiano (antiguas de 7-8 dígitos, actuales de 10); cualquier coincidencia con una cédula real es accidental.

| Cédula | Escenario |
|---|---|
| `1098765432` | Jurado titular en la **misma mesa** donde vota (caso del Figma: Carlos Andrés Martínez, Mesa 018, Colegio Cívico La Esperanza, Medellín). Sin segundo apellido. |
| `1143987654` | Jurado titular en la misma mesa. Nacida un 29 de febrero. |
| `1017234568` | Jurado remanente en **otra mesa del mismo puesto**. Sin segundo nombre; apellido con ñ. |
| `52748193` | Jurado remanente en otra mesa del mismo puesto. Cédula antigua de 8 dígitos. |
| `1036845120` | Jurado titular en **otro puesto** de la misma ciudad. |
| `1023456789` | Solo votante (caso del Figma "Votante sin designación": Laura Camila Gómez, 32 años, Mesa 012, Colegio Cívico La Esperanza, Medellín). Sin segundo apellido. |
| `1144056789` | Solo votante. |
| `79563214` | Solo votante. Cédula antigua de 8 dígitos. |
| `1095827364` | Solo votante. 18 años, género O, sin segundo nombre. |
| `4567891` | Solo votante. Cédula antigua de 7 dígitos, mayor edad. |
| `1000000000` | **No registrada** (no existe en el fixture). |
