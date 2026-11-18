# ADR 0017 · Integración continua en GitHub Actions, con la lógica en `scripts/pruebas.py`

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-11 (commit `c0f680a`, PR #3)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto. Antes de aprobarla preguntó si Jenkins y GitHub Actions eran lo mismo, o si Jenkins se podía agregar después. Aprobó la propuesta con sus cuatro recomendaciones

## Contexto

Correr las suites exigía varios pasos manuales: levantar el backend con un límite de consultas alto, levantar el frontend, correr cada suite y apagar los servidores. Hacía falta que corrieran solas en cada cambio. El dueño del producto también quería poder usar Jenkins más adelante.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| Toda la lógica en el YAML de GitHub Actions | Todo en un archivo | Un futuro Jenkins tendría que repetirla, y en local se correría distinto que en el CI |
| **Un script en Python que hace todo; el YAML solo prepara la máquina y lo llama** | La misma lógica en local, en GitHub Actions y en un futuro Jenkinsfile | Un archivo más que mantener |

## Decisión

- **`scripts/pruebas.py`**, con los comandos `base`, `backend`, `api`, `interfaz` y `todo`, y las opciones `--allure`, `--limpiar-allure`, `--cobertura` y `--browser` (repetible):
  - levanta los servidores que necesita, espera a que respondan y **los apaga siempre**, aunque las pruebas fallen. En Windows cierra el árbol de procesos de npm;
  - **se detiene si el puerto ya está ocupado**, para no correr las pruebas contra otro servidor;
  - devuelve el código de salida de pytest;
  - solo usa la biblioteca estándar y python-dotenv.
- **`.github/workflows/ci.yml`:**
  - corre en cada pull request, en cada push a `main` y a mano;
  - trabajos `backend`, `api`, `frontend`, `interfaz` (uno por navegador, en paralelo y sin cortar los demás si uno falla), `reporte` y `publicar`.
- **Seguridad del CI:**
  - permisos de solo lectura; solo `publicar` puede escribir en Pages;
  - las acciones de GitHub fijadas por versión exacta;
  - sin secretos: la clave de Django se genera en cada corrida, y las contraseñas de MySQL y de los usuarios de demostración solo valen dentro del contenedor temporal.
- **Corridas:** en las ramas de pull request, una corrida nueva cancela la anterior; en `main` no, para no cortar una publicación.
- **Jenkins es opcional:** un `Jenkinsfile` llamaría al mismo script.

## Consecuencias

- **A favor:** local y CI corren exactamente lo mismo, y cambiar de herramienta de CI no exige reescribir la lógica.
- **En contra:** la primera puesta en marcha necesitó cinco corridas por problemas del entorno de GitHub, no del código (ver [ADR 0018](0018-maquinas-del-ci-fijas-e-imagen-de-playwright.md)).

## Cómo se verifica

- **En local (Windows):** `todo --allure` devolvió 0 y apagó los dos servidores. Con el puerto 8000 ocupado se detuvo sin correr pruebas, y con una prueba que fallaba devolvió 1 y apagó el servidor.
- **En GitHub:** cada pull request muestra los seis checks obligatorios (ver [ADR 0019](0019-main-protegida.md)).
