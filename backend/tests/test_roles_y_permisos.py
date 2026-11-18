"""
Pruebas white-box de los roles, los permisos por rol y el admin de Django.

- rol_de(): de dónde sale el rol y quién no tiene ninguno.
- Las clases de permisos que usarán las fases 3 (administración) y 4 (reportes).
- El admin de Django solo admite al superusuario (docs/decisiones/0003).
- La migración 0001_grupos crea los dos roles.
"""
import pytest
from django.contrib import admin
from django.contrib.auth.models import AnonymousUser, Group
from django.test import RequestFactory

from apps.cuentas.permissions import EsAdministrador, EsAnalistaOAdministrador, TieneRolEnLaApp
from apps.cuentas.roles import ADMINISTRADOR, ANALISTA, ROLES, rol_de
from apps.cuentas.sitio_admin import SitioAdminSoloSuperusuario


def test_la_migracion_crea_los_grupos_de_los_roles(db):
    assert set(Group.objects.filter(name__in=ROLES).values_list('name', flat=True)) == {ADMINISTRADOR, ANALISTA}


@pytest.mark.parametrize('rol', [ADMINISTRADOR, ANALISTA])
def test_rol_de_un_usuario_con_rol(crear_usuario, rol):
    assert rol_de(crear_usuario(rol=rol)) == rol


def test_quien_esta_en_los_dos_grupos_es_administrador(crear_usuario):
    usuario = crear_usuario(rol=ANALISTA)
    usuario.groups.add(Group.objects.get(name=ADMINISTRADOR))

    assert rol_de(usuario) == ADMINISTRADOR


@pytest.mark.parametrize('caso', ['sin_grupo', 'desactivado', 'superusuario', 'anonimo', 'ninguno'])
def test_sin_rol_en_la_aplicacion(crear_usuario, caso):
    usuario = {
        'sin_grupo': lambda: crear_usuario(rol=None),
        'desactivado': lambda: crear_usuario(activo=False),
        'superusuario': lambda: crear_usuario(rol=ADMINISTRADOR, superusuario=True),
        'anonimo': AnonymousUser,
        'ninguno': lambda: None,
    }[caso]()

    assert rol_de(usuario) is None


def test_un_grupo_que_no_es_rol_no_da_acceso(crear_usuario):
    usuario = crear_usuario(rol=None)
    usuario.groups.add(Group.objects.create(name='Otro grupo'))

    assert rol_de(usuario) is None


# Matriz de permisos: (clase, permite al administrador, permite al analista).
MATRIZ = [
    (TieneRolEnLaApp, True, True),
    (EsAdministrador, True, False),
    (EsAnalistaOAdministrador, True, True),
]


@pytest.mark.parametrize('permiso, administrador, analista', MATRIZ, ids=lambda valor: getattr(valor, '__name__', None))
def test_matriz_de_permisos_por_rol(crear_usuario, permiso, administrador, analista):
    solicitud = RequestFactory().get('/')

    for rol, esperado in ((ADMINISTRADOR, administrador), (ANALISTA, analista), (None, False)):
        solicitud.user = crear_usuario(usuario=f'usuario.{rol or "sin_rol"}'.lower(), rol=rol)
        assert permiso().has_permission(solicitud, None) is esperado, rol


@pytest.mark.parametrize('permiso', [TieneRolEnLaApp, EsAdministrador, EsAnalistaOAdministrador])
def test_ningun_permiso_admite_al_anonimo_ni_al_superusuario(crear_usuario, permiso):
    solicitud = RequestFactory().get('/')

    for usuario in (AnonymousUser(), crear_usuario(rol=ADMINISTRADOR, superusuario=True)):
        solicitud.user = usuario
        assert permiso().has_permission(solicitud, None) is False


# --- Admin de Django ------------------------------------------------------------------------

@pytest.mark.parametrize('caso', ['administrador_de_la_app', 'analista', 'staff_sin_superusuario', 'administrador_con_staff'])
def test_el_admin_de_django_no_admite_roles_de_la_app_ni_staff(client, crear_usuario, caso):
    """Por defecto Django deja entrar a cualquier is_staff; aquí se exige el superusuario."""
    usuario = {
        'administrador_de_la_app': lambda: crear_usuario(rol=ADMINISTRADOR),
        'analista': lambda: crear_usuario(rol=ANALISTA),
        'staff_sin_superusuario': lambda: crear_usuario(rol=None, staff=True),
        'administrador_con_staff': lambda: crear_usuario(rol=ADMINISTRADOR, staff=True),
    }[caso]()
    client.force_login(usuario)

    respuesta = client.get('/admin/')

    assert respuesta.status_code == 302
    assert respuesta['Location'].startswith('/admin/login/')


def test_el_superusuario_entra_al_admin_de_django(admin_client):
    assert admin_client.get('/admin/').status_code == 200


@pytest.mark.parametrize('activo, superusuario, esperado', [
    (True, True, True), (False, True, False), (True, False, False),
], ids=['superusuario_activo', 'superusuario_desactivado', 'no_superusuario'])
def test_regla_del_sitio_admin(crear_usuario, activo, superusuario, esperado):
    solicitud = RequestFactory().get('/admin/')
    solicitud.user = crear_usuario(rol=None, activo=activo, superusuario=superusuario, staff=True)

    assert admin.site.has_permission(solicitud) is esperado


def test_el_sitio_del_admin_es_el_restringido():
    assert isinstance(admin.site, SitioAdminSoloSuperusuario)
