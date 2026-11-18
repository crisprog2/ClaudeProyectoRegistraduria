"""
Pruebas black-box de la sesión (/api/auth/) contra el servidor en ejecución.

Usan los usuarios de demostración (tests/data/usuarios.json, contraseñas del .env) y
un cliente nuevo por prueba (fixture cliente_sesion), que guarda la cookie del token de
refresco como un navegador. Los casos que exigen cambiar usuarios en la base
(desactivar, quitar el rol, superusuario) y el límite de intentos se prueban en
backend/tests/, porque la suite black-box no toca la base y corre con un límite alto.
"""
from http.cookies import SimpleCookie

import pytest

from support.data_loader import cargar, caso, como_parametros
from support.sesion_client import COOKIE, SESION

pytestmark = pytest.mark.api


def cookie_de(respuesta):
    """Atributos de la cookie del token de refresco en Set-Cookie (un Morsel), o None."""
    galletas = SimpleCookie()
    galletas.load(respuesta.headers.get('Set-Cookie', ''))
    return galletas.get(COOKIE['nombre'])


@pytest.fixture
def analista():
    """Caso del analista de demostración."""
    return caso('usuarios', 'analista')


@pytest.mark.parametrize('usuario', como_parametros('usuarios'))
def test_cada_rol_inicia_sesion(cliente_sesion, usuario):
    respuesta = cliente_sesion.ingresar_como(usuario)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == set(SESION['claves_respuesta_ingreso'])
    assert cuerpo['tipo'] == 'Bearer'
    assert cuerpo['expira_en'] == SESION['expira_en']
    assert cuerpo['usuario'] == usuario['esperado']


@pytest.mark.smoke
def test_la_cookie_del_token_de_refresco_es_segura(cliente_sesion, analista):
    respuesta = cliente_sesion.ingresar_como(analista)

    galleta = cookie_de(respuesta)
    assert galleta is not None
    assert galleta['httponly'] is True
    assert galleta['samesite'] == COOKIE['samesite']
    assert galleta['path'] == COOKIE['ruta']
    assert 0 < int(galleta['max-age']) <= COOKIE['max_age_maximo']
    assert galleta.value not in respuesta.text


@pytest.mark.parametrize('credenciales', como_parametros('credenciales_invalidas'))
def test_credenciales_invalidas(cliente_sesion, mensajes_error, credenciales):
    respuesta = cliente_sesion.enviar_ingreso(credenciales['cuerpo'])

    assert respuesta.status_code == credenciales['http']
    assert respuesta.json() == {'codigo': credenciales['codigo'], 'mensaje': mensajes_error[credenciales['codigo']]}
    assert cookie_de(respuesta) is None


def test_usuario_inexistente_y_contrasena_incorrecta_responden_igual(cliente_sesion):
    """Si respondieran distinto, se podría averiguar qué usuarios existen."""
    inexistente = cliente_sesion.enviar_ingreso(caso('credenciales_invalidas', 'usuario_inexistente')['cuerpo'])
    incorrecta = cliente_sesion.enviar_ingreso(caso('credenciales_invalidas', 'contrasena_incorrecta')['cuerpo'])

    assert (inexistente.status_code, inexistente.json()) == (incorrecta.status_code, incorrecta.json())
    assert inexistente.headers['WWW-Authenticate'] == incorrecta.headers['WWW-Authenticate']


@pytest.mark.smoke
def test_el_token_de_acceso_abre_la_sesion(cliente_sesion, analista):
    acceso = cliente_sesion.ingresar_como(analista).json()['acceso']

    respuesta = cliente_sesion.ver_sesion(acceso)

    assert respuesta.status_code == 200
    assert respuesta.json() == analista['esperado']


@pytest.mark.parametrize('cabecera, codigo', [
    (None, 'NO_AUTENTICADO'),
    ('Bearer esto-no-es-un-jwt', 'TOKEN_INVALIDO'),
    ('Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.firma-inventada', 'TOKEN_INVALIDO'),
], ids=['sin_token', 'basura', 'firma_inventada'])
def test_sesion_sin_un_token_valido(cliente_sesion, mensajes_error, cabecera, codigo):
    respuesta = cliente_sesion.ver_sesion(cabecera_autorizacion=cabecera)

    assert respuesta.status_code == 401
    assert respuesta.json() == {'codigo': codigo, 'mensaje': mensajes_error[codigo]}
    assert respuesta.headers['WWW-Authenticate'].startswith('Bearer')


def test_el_token_de_refresco_no_sirve_como_token_de_acceso(cliente_sesion, analista):
    cliente_sesion.ingresar_como(analista)

    respuesta = cliente_sesion.ver_sesion(cliente_sesion.cookie_refresco)

    assert respuesta.status_code == 401
    assert respuesta.json()['codigo'] == 'TOKEN_INVALIDO'


def test_renovar_la_sesion_rota_la_cookie(cliente_sesion, analista):
    cliente_sesion.ingresar_como(analista)
    original = cliente_sesion.cookie_refresco

    respuesta = cliente_sesion.refrescar()

    assert respuesta.status_code == 200
    assert cliente_sesion.ver_sesion(respuesta.json()['acceso']).status_code == 200
    assert cliente_sesion.cookie_refresco not in (None, original)


def test_una_cookie_rotada_ya_no_sirve(cliente_sesion, analista, mensajes_error):
    cliente_sesion.ingresar_como(analista)
    original = cliente_sesion.cookie_refresco
    cliente_sesion.refrescar()
    cliente_sesion.poner_cookie_refresco(original)

    respuesta = cliente_sesion.refrescar()

    assert respuesta.status_code == 401
    assert respuesta.json() == {'codigo': 'SESION_EXPIRADA', 'mensaje': mensajes_error['SESION_EXPIRADA']}


@pytest.mark.smoke
def test_cerrar_sesion_revoca_la_cookie(cliente_sesion, analista):
    cliente_sesion.ingresar_como(analista)
    original = cliente_sesion.cookie_refresco

    respuesta = cliente_sesion.salir()

    assert respuesta.status_code == 204
    assert cliente_sesion.cookie_refresco is None
    cliente_sesion.poner_cookie_refresco(original)
    assert cliente_sesion.refrescar().status_code == 401


def test_renovar_sin_haber_iniciado_sesion(cliente_sesion):
    respuesta = cliente_sesion.refrescar()

    assert respuesta.status_code == 401
    assert respuesta.json()['codigo'] == 'SESION_EXPIRADA'


@pytest.mark.parametrize('accion', ['refrescar', 'salir'])
def test_renovar_y_salir_exigen_la_cabecera_de_la_aplicacion(cliente_sesion, analista, mensajes_error, accion):
    """Protección contra CSRF: sin la cabecera propia se rechaza, aunque la cookie sea válida."""
    cliente_sesion.ingresar_como(analista)

    respuesta = getattr(cliente_sesion, accion)(con_cabecera=False)

    assert respuesta.status_code == 403
    assert respuesta.json() == {'codigo': 'SOLICITUD_RECHAZADA', 'mensaje': mensajes_error['SOLICITUD_RECHAZADA']}
    assert cliente_sesion.refrescar().status_code == 200


@pytest.mark.parametrize('ruta', ['ingresar', 'refrescar', 'salir'])
def test_rutas_de_post_rechazan_get(cliente_sesion, ruta):
    respuesta = cliente_sesion.pedir('GET', ruta)

    assert respuesta.status_code == 405
    assert respuesta.json() == {
        'codigo': 'METODO_NO_PERMITIDO',
        'mensaje': SESION['mensaje_metodo_no_permitido']['POST'],
    }
    assert 'POST' in respuesta.headers['Allow']


def test_ingresar_solo_acepta_json(cliente_sesion, mensajes_error):
    respuesta = cliente_sesion.pedir('POST', 'ingresar', data={'usuario': 'analista.demo', 'contrasena': 'x'})

    assert respuesta.status_code == 415
    assert respuesta.json() == {'codigo': 'SOLICITUD_INVALIDA', 'mensaje': mensajes_error['SOLICITUD_INVALIDA']}


@pytest.mark.smoke
def test_la_consulta_publica_no_exige_sesion(api):
    """La consulta sigue abierta: sin token y con un token inválido responde igual."""
    cedula = cargar('ciudadanos')[0]['cedula']

    sin_token = api.consultar(cedula)
    con_token_invalido = api.enviar('POST', json={'cedula': cedula}, headers={'Authorization': 'Bearer basura'})

    assert sin_token.status_code == con_token_invalido.status_code == 200
    assert sin_token.json() == con_token_invalido.json()
