# ADR 0015 · PyMySQL en lugar de mysqlclient

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-09 (commit `8694003`)
- **Documentado:** 2026-11-18, a posteriori, a partir del mensaje del commit, el README (paso 1, "Controlador de MySQL") y `CLAUDE.md`
- **Aprobada por:** el dueño del producto

## Contexto

Django recomienda `mysqlclient` para MySQL, un controlador con un componente compilado en C (`_mysql.pyd`). El 2026-11-09, el **Control inteligente de aplicaciones de Windows 11**, activo en el equipo del dueño del producto, bloqueó ese componente porque no tiene firma digital. El backend dejó de arrancar con el error *"Una directiva de Control de aplicaciones bloqueó este archivo"*.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| Desactivar el Control inteligente de aplicaciones | `mysqlclient` vuelve a funcionar | Baja la seguridad del equipo, y Windows no permite volver a activarlo sin reinstalar. Decisión que corresponde al dueño del equipo, que no la tomó |
| **PyMySQL** | Escrito solo en Python: no hay nada compilado que bloquear. Se registra como `MySQLdb`, así que Django lo usa sin otros cambios | Django no lo soporta oficialmente; algo más lento (irrelevante aquí) |

## Decisión

- **PyMySQL 1.2.3** reemplaza a `mysqlclient` 2.3.0, en local y en el CI.
- Se registra en `backend/config/__init__.py` con `pymysql.install_as_MySQLdb()`.
- **Que Django no lo soporte oficialmente lo compensan las pruebas:** todas las pruebas white-box corren contra MySQL, y una verifica que la conexión use PyMySQL.
- **Sin `cryptography`:** la conexión local sale cifrada con TLS, así que el método de autenticación `caching_sha2_password` de MySQL 8 funciona sin instalarlo. En el CI también funcionó con el contenedor `mysql:8.0`.
- **No se desactiva la protección de Windows** sin que el dueño del producto lo decida.

## Consecuencias

- **A favor:** el backend arranca en el equipo protegido sin bajar su seguridad.
- **En contra:** si una versión futura de Django dejara de ser compatible con PyMySQL, lo detectarían las pruebas.
- **Relacionado:** la misma protección de Windows bloqueó una vez archivos de WebKit (`JavaScriptCore.dll`, `sqlite3.dll`). Si WebKit falla en bloque, hay que revisar primero los eventos 3077 del registro *Microsoft-Windows-CodeIntegrity/Operational* (comando en el README).

## Cómo se verifica

- `backend/tests/test_configuracion.py`: `test_la_conexion_usa_pymysql`.
- El CI corre todas las suites con PyMySQL contra `mysql:8.0`.
