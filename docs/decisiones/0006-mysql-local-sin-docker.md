# ADR 0006 · MySQL 8.0 local sin Docker, y un contenedor solo en el CI

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 (commit `4b15d73`). El CI se agregó el 2026-11-11 (commit `c0f680a`)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md` y el historial de Git
- **Aprobada por:** el dueño del producto. Al inicio se había sugerido Docker; más adelante volvió a preguntar si convenía cambiar y siguió con la base local

## Contexto

El backend necesita MySQL. El equipo del dueño del producto tiene MySQL 8.0 instalado como servicio de Windows, y no tiene Docker ni WSL.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **Servidor local ya instalado** | Sin instalar nada más; el dueño lo conoce y lo administra | El entorno no se crea con un comando: hay que crear la base y el usuario a mano, una vez |
| Docker con `mysql:8.0` | Entorno reproducible con un comando | Exigía instalar Docker Desktop y WSL en el equipo |
| SQLite para las pruebas | Rápido y sin servidor | Se comporta distinto que MySQL: modo estricto, largos máximos y collation. Las pruebas podrían pasar y la aplicación fallar |

## Decisión

- **En local:** el MySQL 8.0 del equipo (puerto 3306), con la base `registraduria` (`utf8mb4_0900_ai_ci`, modo estricto) y un usuario propio, `consultavoto_app`, que solo tiene permisos sobre `registraduria` y `test_registraduria`, sin permisos de administrador.
- **En las pruebas:** también MySQL. pytest-django crea y borra `test_registraduria` en cada corrida, con el mismo charset y la misma collation.
- **En el CI:** un contenedor `mysql:8.0` nuevo por trabajo, como servicio de GitHub Actions, para mantener la misma versión mayor sin depender del equipo local.
- Las acciones que exigen la contraseña de root de MySQL las hace el dueño del producto.

## Consecuencias

- **A favor:** las pruebas corren contra el mismo motor que la aplicación, y el CI usa una base limpia en cada trabajo.
- **En contra:** la puesta en marcha local tiene pasos manuales, documentados en el README (paso 2).
- Esta decisión hizo visible el problema de [ADR 0015](0015-pymysql-en-lugar-de-mysqlclient.md): el controlador compilado de MySQL lo bloqueó Windows en el equipo local.

## Cómo se verifica

- `backend/tests/test_configuracion.py`: la conexión usa el controlador esperado.
- Todas las pruebas white-box corren contra MySQL, en local y en el CI.
