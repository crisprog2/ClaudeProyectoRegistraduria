"""
Pruebas white-box del comando crear_usuarios_demo.

Las contraseñas solo vienen de variables de entorno: aquí se fijan con monkeypatch
para no depender del .env. Se verifica también que los mensajes de error nunca
muestren la contraseña.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command

from apps.cuentas.roles import ADMINISTRADOR, ANALISTA, rol_de

CONTRASENAS = {'DEMO_ADMIN_CONTRASENA': 'Clave-Admin-Prueba-2026', 'DEMO_ANALISTA_CONTRASENA': 'Clave-Analista-Prueba-2026'}


@pytest.fixture
def con_contrasenas(monkeypatch):
    """Variables de entorno de las contraseñas de demostración, válidas."""
    for variable, valor in CONTRASENAS.items():
        monkeypatch.setenv(variable, valor)


def usuario(nombre):
    """Usuario de la base por su nombre de usuario."""
    return get_user_model().objects.get(username=nombre)


def test_crea_un_usuario_por_rol(db, con_contrasenas):
    call_command('crear_usuarios_demo')

    administrador, analista = usuario('admin.demo'), usuario('analista.demo')
    assert rol_de(administrador) == ADMINISTRADOR
    assert rol_de(analista) == ANALISTA
    assert administrador.check_password(CONTRASENAS['DEMO_ADMIN_CONTRASENA'])
    assert analista.check_password(CONTRASENAS['DEMO_ANALISTA_CONTRASENA'])


def test_los_usuarios_demo_no_entran_al_admin_de_django(db, con_contrasenas):
    call_command('crear_usuarios_demo')

    for nombre in ('admin.demo', 'analista.demo'):
        cuenta = usuario(nombre)
        assert not cuenta.is_staff
        assert not cuenta.is_superuser


def test_se_puede_correr_varias_veces_y_restaura_el_estado(db, con_contrasenas, monkeypatch):
    call_command('crear_usuarios_demo')
    get_user_model().objects.filter(username='analista.demo').update(is_active=False, is_staff=True)
    monkeypatch.setenv('DEMO_ANALISTA_CONTRASENA', 'Clave-Nueva-Analista-2026')

    call_command('crear_usuarios_demo')

    analista = usuario('analista.demo')
    assert get_user_model().objects.filter(username__endswith='.demo').count() == 2
    assert analista.is_active and not analista.is_staff
    assert analista.check_password('Clave-Nueva-Analista-2026')
    assert list(analista.groups.values_list('name', flat=True)) == [ANALISTA]


@pytest.mark.parametrize('variable', list(CONTRASENAS))
def test_sin_la_variable_de_entorno_falla_sin_crear_nada(db, con_contrasenas, monkeypatch, variable):
    monkeypatch.delenv(variable)

    with pytest.raises(CommandError, match=variable):
        call_command('crear_usuarios_demo')

    assert not get_user_model().objects.filter(username__endswith='.demo').exists()


# La corta no es una palabra, para que no pueda aparecer en el mensaje de Django ("...es demasiado corta").
@pytest.mark.parametrize('contrasena', ['12345678', 'Xq7#k', 'password'], ids=['solo_numeros', 'corta', 'comun'])
def test_contrasena_que_no_cumple_las_reglas(db, con_contrasenas, monkeypatch, contrasena):
    monkeypatch.setenv('DEMO_ADMIN_CONTRASENA', contrasena)

    with pytest.raises(CommandError, match='no cumple las reglas') as error:
        call_command('crear_usuarios_demo')

    assert contrasena not in str(error.value)
    assert not get_user_model().objects.filter(username__endswith='.demo').exists()
