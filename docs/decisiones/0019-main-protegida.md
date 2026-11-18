# ADR 0019 · `main` protegida: todo cambio entra por pull request con el CI en verde

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-11 (ruleset "Proteger main"; documentado en el PR #4)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto, que creó la protección en GitHub

## Contexto

Con el CI funcionando, nada impedía todavía subir cambios directamente a `main` sin que pasaran las pruebas, ni reescribir su historial. Un solo push con un error dejaría la rama principal rota y el reporte publicado con fallas.

## Decisión

Un **ruleset de GitHub ("Proteger main")** que:

- **exige un pull request** con 0 aprobaciones: el dueño del producto trabaja solo, y GitHub no deja aprobar un pull request propio;
- **exige que pasen los 6 checks de pruebas:** `Backend (white-box)`, `API y BDD por la API`, `Frontend (build)`, `Interfaz (chromium)`, `Interfaz (firefox)` e `Interfaz (webkit)`. "Reporte de Allure" no es obligatorio, porque pasa aunque fallen las pruebas;
- **exige que la rama esté al día con `main`;**
- **prohíbe borrar `main` y el force push.**

**Flujo de trabajo:**
1. Cada cambio, incluida la documentación, va en una rama (`feature/...`, `fix/...`, `docs/...`).
2. El dueño del producto abre el pull request y hace el merge con el CI en verde.
3. Claude no hace commit ni push sin que se lo pidan.

## Consecuencias

- **A favor:** `main` siempre pasa todas las pruebas, y su historial no se puede reescribir.
- **En contra:**
  - hasta un cambio de una línea de documentación pasa por un pull request y una corrida completa del CI;
  - **si se renombra un trabajo del workflow, hay que actualizar el ruleset**, o los pull requests quedarán esperando un check que ya no existe;
  - la regla de pull request trae activa por defecto `require_extra_approval_for_unattributed_changes`: si un pull request se bloquea pidiendo aprobación con el CI en verde, hay que revisar eso primero.

## Cómo se verifica

- Sin autenticación, con `GET /repos/crisprog2/ClaudeProyectoRegistraduria/rules/branches/main`. La API pública no muestra la lista de excepciones (*bypass*).
- Desde que existe el ruleset, cada pull request se fusionó solo con los seis checks en verde.
