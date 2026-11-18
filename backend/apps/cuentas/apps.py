"""Configuración de la app 'cuentas'."""
from django.apps import AppConfig


class CuentasConfig(AppConfig):
    """
    Usuarios de la aplicación: inicio de sesión con JWT, roles y permisos.

    No define modelos propios: usa las tablas de Django (auth_user, auth_group y
    auth_user_groups) y las de simplejwt para los tokens revocados. Ver docs/decisiones/0001.
    El admin de Django restringido al superusuario está en sitio_admin.py.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cuentas'
    label = 'cuentas'
    verbose_name = 'Cuentas y roles'
