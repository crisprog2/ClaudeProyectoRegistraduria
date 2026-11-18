"""
Roles de la aplicación.

Cada rol es un grupo de Django (tabla auth_group), creado por la migración
0001_grupos. Un usuario tiene un rol si pertenece a su grupo (auth_user_groups).

- Administrador: edita los datos, gestiona usuarios y ve el reporte.
- Analista: solo ve el reporte.

El superusuario no tiene rol en la aplicación: solo usa el admin de Django.
"""
from django.contrib.auth.models import Group

ADMINISTRADOR = 'Administrador'
ANALISTA = 'Analista'

# En orden de prioridad: si alguien estuviera en los dos grupos, se le trata como administrador.
ROLES = (ADMINISTRADOR, ANALISTA)


def rol_de(usuario):
    """
    Rol del usuario en la aplicación, leído de la base de datos en cada llamada, o None.

    None si el usuario no existe, está inactivo, es superusuario o no pertenece a
    ningún grupo de rol. Leerlo siempre de la base (y no del token) hace que quitar
    un rol o desactivar a alguien tenga efecto inmediato.
    """
    if usuario is None or not usuario.is_authenticated or not usuario.is_active or usuario.is_superuser:
        return None
    grupos = set(Group.objects.filter(user=usuario, name__in=ROLES).values_list('name', flat=True))
    return next((rol for rol in ROLES if rol in grupos), None)
