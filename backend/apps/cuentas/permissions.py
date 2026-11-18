"""
Permisos de DRF por rol.

Se usan en las vistas protegidas, junto con la autenticación JWT por defecto
(REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']). El rol se lee de la base en cada
petición (roles.rol_de), no del token: quitar un rol tiene efecto inmediato.

Sin token o con un token inválido, DRF responde 401 (NO_AUTENTICADO o TOKEN_INVALIDO)
antes de llegar aquí. Con un token válido y sin el rol necesario, responde 403 (SIN_PERMISO).
"""
from rest_framework.permissions import BasePermission

from .roles import ADMINISTRADOR, ANALISTA, ROLES, rol_de


class TieneRol(BasePermission):
    """Base: permite la petición si el rol del usuario está en `roles`."""
    roles = ROLES

    def has_permission(self, request, view):
        """True si el usuario autenticado tiene alguno de los roles permitidos."""
        return rol_de(request.user) in self.roles


class TieneRolEnLaApp(TieneRol):
    """Cualquier usuario con rol en la aplicación: administrador o analista."""


class EsAdministrador(TieneRol):
    """Solo el administrador: edición de datos y gestión de usuarios (fases 3 y 6)."""
    roles = (ADMINISTRADOR,)


class EsAnalistaOAdministrador(TieneRol):
    """El analista y el administrador: el reporte de consultas (fases 4 y 7)."""
    roles = (ANALISTA, ADMINISTRADOR)
