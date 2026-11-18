# ADR 0018 · Máquinas del CI fijas en Ubuntu 24.04 y pruebas de interfaz en la imagen oficial de Playwright

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-11 (commits `810ae7e`, `1d64a8f`, `7e5a178` y `ca1d177`, PR #3)
- **Documentado:** 2026-11-18, a posteriori, a partir de los mensajes de los commits y `CLAUDE.md`
- **Aprobada por:** el dueño del producto, que compartió los errores de cada corrida y aprobó cada corrección

## Contexto

En la primera corrida del CI, `ubuntu-latest` ya era Ubuntu 26.04. `playwright install --with-deps`, que instala los navegadores y sus librerías con `apt`, falló con *"Temporary failure resolving 'archive.ubuntu.com'"*. Chromium falló a los 11 minutos, y Firefox y WebKit se cortaron a los 30. El backend, la API y el frontend sí pasaron.

## Puesta en marcha (cinco corridas)

| Corrida | Cambio | Resultado |
|---|---|---|
| 1 | `ubuntu-latest` (26.04) | `apt` no resolvió los servidores de Ubuntu |
| 2 | Fijar `ubuntu-24.04` y 3 reintentos | Igual (*"azure.archive.ubuntu.com"*), con GitHub reportando todo operativo. **Conclusión:** las máquinas no resolvían los servidores de paquetes de Ubuntu, fuera cual fuera la versión |
| 3 | Correr la interfaz dentro de la imagen oficial de Playwright, que ya trae los navegadores y sus librerías | Falló la caché de pip: su script apunta a una ruta que dentro del contenedor está en otro lugar |
| 4 | Sin caché de pip en esos trabajos, e instalar con `python -m pip` | Pasaron Chromium y WebKit. Firefox no arrancó: *"Firefox is unable to launch if the $HOME folder isn't owned by the current user"* |
| 5 | `HOME: /root` en los trabajos de interfaz (la solución que indica el propio mensaje) | **Los siete trabajos pasaron** |

## Decisión

- **Todas las máquinas en `ubuntu-24.04`**, no `ubuntu-latest`, para que el CI no cambie de sistema sin aviso.
- **Los trabajos de interfaz corren dentro de `mcr.microsoft.com/playwright/python:v1.64.1-noble`**, con la misma versión de Playwright que `tests/requirements.txt`. No usan `apt`. Opción `--ipc=host`, recomendada para Chromium.
- **Dentro del contenedor:**
  - MySQL se alcanza por el nombre del servicio (`MYSQL_HOST: mysql`);
  - `HOME: /root`;
  - sin caché de pip;
  - los permisos de la base de pruebas se dan con PyMySQL, porque dentro de un contenedor no existe `docker exec`.

## Consecuencias

- **A favor:** el CI es estable y no depende de los servidores de paquetes de Ubuntu. Una corrida completa tarda unos 5 minutos, porque los trabajos corren en paralelo.
- **En contra:**
  - **si se actualiza Playwright, hay que actualizar también la etiqueta de la imagen;**
  - los trabajos de interfaz no tienen caché de pip y tardan un poco más.

## Cómo se verifica

- Cada corrida del CI. La primera exitosa fue la 43059436476 (2026-11-11). Ahí se confirmó también que PyMySQL funciona sin `cryptography` dentro del contenedor y que las pruebas de pantallas pequeñas pasan con las fuentes de Linux.
