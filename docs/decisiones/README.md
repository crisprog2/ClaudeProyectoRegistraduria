# Registro de decisiones de arquitectura (ADR)

Cada archivo de esta carpeta explica **una decisión importante** del proyecto: qué problema había, qué opciones se consideraron, qué se eligió, qué consecuencias tiene y qué pruebas la protegen. Es una práctica común en equipos de software (*Architecture Decision Records*): el código muestra **qué** se hizo; estos documentos explican **por qué**.

Las decisiones las aprueba el dueño del producto antes de implementarlas. Si una decisión cambia, no se borra su ADR: se escribe uno nuevo que lo reemplaza y el anterior pasa a estado "Reemplazada".

## Cómo leer los números

**El número indica el orden en que se escribió cada ADR, no la fecha de la decisión.**

- **0001 a 0003** se escribieron junto con su decisión, en la fase 1 de roles y acceso.
- **0004 a 0022 son retroactivos:** documentan, el 2026-11-18, decisiones tomadas desde el 2026-11-03. Se reconstruyeron con `CLAUDE.md`, el README y el historial de Git, y cada uno cita los commits donde se tomó la decisión.

En los ADR retroactivos, "Opciones consideradas" incluye las alternativas habituales para cada tema. Cuando una alternativa se discutió con el dueño del producto (Docker, un servicio de mapas, Jenkins, desactivar la protección de Windows), el ADR lo dice.

## Decisiones, en orden cronológico

| Fecha | N.º | Decisión | Tema |
|---|---|---|---|
| 2026-11-03 | [0004](0004-marca-ficticia-y-datos-inventados.md) | Marca ficticia y solo datos inventados | Producto |
| 2026-11-03 | [0005](0005-stack-django-lts-y-versiones-fijas.md) | Django 5.2 LTS con Python 3.11 y versiones fijadas | Arquitectura |
| 2026-11-03 | [0006](0006-mysql-local-sin-docker.md) | MySQL 8.0 local sin Docker, y un contenedor solo en el CI | Arquitectura |
| 2026-11-03 | [0007](0007-modelo-de-datos.md) | Modelo de datos: jurado por designación, edad calculada y referencias protegidas | Datos |
| 2026-11-03 | [0008](0008-cedula-nunca-en-la-url.md) | La cédula nunca viaja en la URL | Privacidad |
| 2026-11-03 | [0009](0009-formato-unico-de-errores.md) | Un solo formato de error: `{"codigo", "mensaje"}` | API |
| 2026-11-03 | [0010](0010-limite-de-consultas-por-ip.md) | Límite de consultas por IP, sin confiar en `X-Forwarded-For` | Seguridad |
| 2026-11-03 | [0022](0022-pruebas-de-mutacion.md) | Toda regla importante se comprueba también con una prueba de mutación | Calidad |
| 2026-11-03 a 06 | [0011](0011-estrategia-de-pruebas.md) | Estrategia de pruebas: cuatro niveles en Python, BDD en español por dos canales y Page Objects accesibles | Calidad |
| 2026-11-03 a 04 | [0012](0012-frontend-sin-servicios-externos.md) | Frontend sin servicios externos: un solo origen, fuente local y mapa ilustrativo | Frontend |
| 2026-11-03 a 04 | [0013](0013-figma-como-referencia-y-sus-excepciones.md) | El Figma como referencia, y cuándo apartarse de él | Diseño |
| 2026-11-06 | [0014](0014-swagger-servido-desde-el-proyecto.md) | Documentación OpenAPI 3.1 con Swagger UI servido desde el proyecto, y probada | API |
| 2026-11-09 | [0015](0015-pymysql-en-lugar-de-mysqlclient.md) | PyMySQL en lugar de mysqlclient | Arquitectura |
| 2026-11-09 | [0016](0016-allure-3-sin-java.md) | Un solo reporte de Allure 3, sin Java, con solo allure-pytest | Calidad |
| 2026-11-11 | [0017](0017-ci-con-la-logica-en-un-script.md) | Integración continua en GitHub Actions, con la lógica en `scripts/pruebas.py` | CI |
| 2026-11-11 | [0018](0018-maquinas-del-ci-fijas-e-imagen-de-playwright.md) | Máquinas del CI fijas en Ubuntu 24.04 y pruebas de interfaz en la imagen de Playwright | CI |
| 2026-11-11 | [0019](0019-main-protegida.md) | `main` protegida: todo cambio entra por pull request con el CI en verde | Proceso |
| 2026-11-12 | [0020](0020-reporte-publicado-con-historial.md) | Reporte publicado en GitHub Pages, con el historial en el propio sitio | CI |
| 2026-11-17 | [0021](0021-cobertura-con-minimo-del-95.md) | Cobertura de código del backend, con ramas y un mínimo del 95 % | Calidad |
| 2026-11-18 | [0001](0001-roles-y-administracion-propia.md) | Roles Administrador y Analista, y administración en una pantalla propia | Roles y acceso · fase 1 |
| 2026-11-18 | [0002](0002-tokens-en-memoria-y-cookie-httponly.md) | Token de acceso en memoria y token de refresco en una cookie HttpOnly | Roles y acceso · fase 1 |
| 2026-11-18 | [0003](0003-admin-de-django-solo-superusuario.md) | El admin de Django queda solo para el superusuario | Roles y acceso · fase 1 |

Todas están en estado **Aceptada**.

## Formato

Cada ADR tiene las mismas secciones:

- **Estado, fecha y aprobación.** Los retroactivos tienen además "Documentado" y los commits de la decisión.
- **Contexto:** la situación y el problema.
- **Opciones consideradas**, con sus ventajas y desventajas.
- **Decisión.**
- **Consecuencias:** lo que se gana, lo que se pierde y los límites conocidos.
- **Cómo se verifica:** las pruebas que fallarían si alguien deshiciera la decisión por error.

Para agregar uno nuevo: usar el número siguiente libre (hoy, 0023), seguir este formato y agregarlo a la tabla.
