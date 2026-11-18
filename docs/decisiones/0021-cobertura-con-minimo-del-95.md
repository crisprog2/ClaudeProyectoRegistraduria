# ADR 0021 · Cobertura de código del backend, con ramas y un mínimo del 95 %

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-17 (commit `0d3f65b`, PR #8)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto. Antes de aprobarla preguntó qué hacía exactamente, si era buena práctica y si convenía implementarla antes de otras funcionalidades, como JWT. Eligió el mínimo del 95 % y publicar el HTML junto al reporte de Allure

## Contexto

No había forma de saber qué código del backend no ejecutaba ninguna prueba, ni de evitar que llegara código nuevo sin pruebas. Se iban a agregar funcionalidades grandes (JWT y roles), así que convenía medir antes, sobre una base estable.

## Opciones consideradas

| Tema | Alternativas | Elegida y por qué |
|---|---|---|
| Qué medir | Solo líneas, o líneas y ramas | **Líneas y ramas:** un `if` debe probarse por sus dos caminos |
| Alcance | Backend; backend medido también desde las pruebas black-box; frontend | **Solo el backend con las pruebas white-box** (fase 1). Medirlo desde las pruebas black-box exige apagar el servidor de forma ordenada; el frontend exige instrumentar el código, porque Playwright para Python no expone la cobertura del navegador |
| Mínimo | 100 %, 90 %, sin mínimo | **95 %:** deja margen para cambios pequeños y detecta un módulo nuevo sin pruebas |
| Cuándo medir | En cada `pytest` (`addopts`) o bajo demanda | **Bajo demanda** (`--cobertura`): si se midiera siempre, correr una sola prueba fallaría por cobertura baja |
| Momento | Antes o después de JWT | **Antes:** cada funcionalidad nueva muestra su propio efecto sobre la cobertura |

## Decisión

- **`pytest-cov` 7.1.0 y `coverage` 7.17.3**, fijadas las dos.
- **`backend/.coveragerc`:** mide `apps` y `config` con ramas, con `fail_under = 95`. Excluye las migraciones, `settings/local.py`, `asgi.py` y `wsgi.py`, cada una con su motivo.
- **`scripts/pruebas.py backend --cobertura`** (y `todo --cobertura`) genera la tabla en la terminal, el HTML en `reportes/cobertura/` y `coverage.xml`.
- **En el CI:**
  - el trabajo del backend falla si la cobertura baja del mínimo;
  - la tabla aparece en el resumen de la corrida;
  - el HTML se guarda como artefacto y el de `main` se publica en `/cobertura/`.

  No hay un check nuevo: no hizo falta cambiar el ruleset.
- **Antes de fijar el mínimo se midió:** 92 %. Se agregaron 39 pruebas para cubrir lo que faltaba: el admin, los `__str__`, los errores de configuración y el manejador de errores. Cada una verifica un comportamiento concreto, no solo suma líneas. Quedó en 100 %.
- **Convención:** el código nuevo llega con sus pruebas. Excluir un archivo o bajar el mínimo exige un motivo escrito en `.coveragerc` y en el pull request.

## Consecuencias

- **A favor:**
  - un pull request con código sin probar no se puede fusionar;
  - el HTML público muestra qué cubre cada prueba.
- **En contra:**
  - la cobertura dice qué código se ejecuta, no si las pruebas lo verifican. Por eso las reglas importantes se comprueban también con mutación (ver [ADR 0022](0022-pruebas-de-mutacion.md));
  - medir agrega unos segundos a las pruebas del backend.

## Cómo se verifica

- **Mutación verificada:** un módulo nuevo sin pruebas baja la cobertura a 92,2 % y el comando termina con código 1, aunque las 136 pruebas de entonces pasaran.
- **En el CI:** 100 % en la corrida sobre `main` (342 líneas y 24 ramas). Con la fase 1 de roles sigue en 100 % (627 líneas y 48 ramas).
