# ADR 0003 · El admin de Django queda solo para el superusuario

- **Estado:** Aceptada
- **Fecha:** 2026-11-18
- **Aprobada por:** el dueño del producto
- **Fase:** 1 · Autenticación y roles

## Contexto

El proyecto ya tenía configurado el admin de Django (`/admin/`) para revisar los datos de demostración. Con la administración propia del producto (ver [ADR 0001](0001-roles-y-administracion-propia.md)), había que decidir qué pasaba con él.

Por defecto, Django deja entrar al admin a **cualquier usuario con `is_staff`**, no solo al superusuario. Si alguien marcara por error a un administrador o analista de la aplicación como `is_staff`, ese usuario podría editar cualquier tabla desde el admin de Django y saltarse todas las reglas de la aplicación.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Quitar el admin de Django** | Una sola forma de administrar | Se pierde una herramienta de soporte útil y ya probada |
| **B. Dejarlo como está** | Nada que hacer | Cualquier `is_staff` entra |
| **C. Dejarlo solo para el superusuario** | Se conserva para soporte y se cierra la puerta a los demás | Un pequeño cambio de configuración |

## Decisión

**Opción C.** El admin de Django es una **herramienta interna de soporte**, solo para el superusuario. La administración oficial del producto es la pantalla propia.

Cómo se implementa:

- `apps/cuentas/sitio_admin.py` define `SitioAdminSoloSuperusuario`, un `AdminSite` cuyo permiso exige un superusuario activo.
- En `INSTALLED_APPS`, `'django.contrib.admin'` se reemplaza por `'apps.cuentas.sitio_admin.AdminSoloSuperusuarioConfig'`, la forma que documenta Django para cambiar el sitio por defecto. Los `admin.register` existentes no cambian.
- Los usuarios de demostración (`crear_usuarios_demo`) se crean siempre con `is_staff` e `is_superuser` en falso.
- El superusuario, a su vez, no puede entrar a la aplicación (ADR 0001): cada uno usa su herramienta.

## Consecuencias

- **A favor:** un error al marcar `is_staff` ya no abre el admin, y se conserva la herramienta de soporte.
- **En contra:** ninguna relevante. Si en el futuro hiciera falta dar acceso al admin a alguien más, habría que cambiar esta decisión con un ADR nuevo.

## Cómo se verifica

- `backend/tests/test_roles_y_permisos.py`:
  - un administrador, un analista, un usuario solo `is_staff` y un administrador con `is_staff` son redirigidos al inicio de sesión del admin;
  - el superusuario entra;
  - la regla del sitio con un superusuario activo, uno desactivado y un usuario que no es superusuario;
  - el sitio en uso es el restringido.
- `backend/tests/test_usuarios_demo.py`: los usuarios de demostración no son `is_staff` ni superusuarios.
- **Mutación verificada:** si el sitio volviera a admitir cualquier `is_staff`, fallarían 3 pruebas.
