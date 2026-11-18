"""
Admin de Django que solo admite al superusuario.

El admin de Django queda como herramienta interna de soporte (docs/decisiones/0003).
La administración del producto es la pantalla propia de la aplicación, con los roles
Administrador y Analista. Por defecto Django deja entrar a cualquier usuario con
is_staff; aquí se exige además is_superuser, para que un rol de la aplicación nunca
abra el admin aunque alguien le active is_staff por error.

Se activa en INSTALLED_APPS con 'apps.cuentas.sitio_admin.AdminSoloSuperusuarioConfig'
en lugar de 'django.contrib.admin'. Vive aquí y no en apps.py porque Django no admite
dos configuraciones de app en el mismo módulo apps.py.
"""
from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig


class SitioAdminSoloSuperusuario(AdminSite):
    """AdminSite que exige un superusuario activo."""

    def has_permission(self, request):
        """True solo para un superusuario activo."""
        return request.user.is_active and request.user.is_superuser


class AdminSoloSuperusuarioConfig(AdminConfig):
    """Configuración de django.contrib.admin que usa SitioAdminSoloSuperusuario como sitio por defecto."""
    default_site = 'apps.cuentas.sitio_admin.SitioAdminSoloSuperusuario'
