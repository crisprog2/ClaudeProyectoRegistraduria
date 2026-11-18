# ADR 0005 · Django 5.2 LTS con Python 3.11 y versiones fijadas

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 (commits `d866bc1` y `50c8ada`)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md` y el historial de Git
- **Aprobada por:** el dueño del producto

## Contexto

Hacía falta un backend con una API REST y un frontend de una sola página. El equipo tenía instalado Python 3.11. En un proyecto de pruebas, que las dependencias cambien solas entre una corrida y otra produce fallas que no tienen que ver con el código.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| Django 6 | La versión más nueva | Exige Python 3.12 o superior; obligaba a cambiar el Python del equipo |
| **Django 5.2 LTS** | Soporte extendido de seguridad, compatible con Python 3.11 | No trae las novedades de Django 6 |
| Rangos de versiones (`>=`, `^`) | Actualizaciones automáticas | Una corrida puede fallar por una versión nueva y no por el código |
| **Versiones exactas** (`==` en pip, sin `^` en npm, `package-lock.json` versionado) | Corridas repetibles en el equipo local y en el CI | Las actualizaciones se hacen a mano |

## Decisión

- **Backend:** Python 3.11, Django 5.2 LTS, Django REST Framework y MySQL 8.0. **No subir a Django 6** mientras el proyecto use Python 3.11.
- **Frontend:** React con Vite y react-router-dom.
- **Un solo entorno virtual** en la raíz (`.venv/`) para el backend y las pruebas.
- **Versiones exactas** en `backend/requirements.txt`, `tests/requirements.txt`, `frontend/package.json` y `reportes/package.json`, con sus archivos de bloqueo versionados.
- Cuando el resultado de una herramienta depende de una dependencia transitiva, esa también se fija: `coverage` junto a `pytest-cov`, y `PyJWT` junto a `djangorestframework-simplejwt`.

## Consecuencias

- **A favor:** las corridas son repetibles; un cambio de comportamiento siempre viene de un cambio en el repositorio.
- **En contra:** actualizar exige un cambio explícito, con su pull request y su corrida del CI. Las acciones de GitHub también se fijan por versión exacta (ver [ADR 0017](0017-ci-con-la-logica-en-un-script.md)), y la imagen de Playwright del CI debe coincidir con la versión de `tests/requirements.txt` (ver [ADR 0018](0018-maquinas-del-ci-fijas-e-imagen-de-playwright.md)).

## Cómo se verifica

- El CI instala con `pip install -r` y `npm ci`, que respetan exactamente las versiones fijadas. Si un archivo de bloqueo no coincide con su `package.json`, `npm ci` falla.
