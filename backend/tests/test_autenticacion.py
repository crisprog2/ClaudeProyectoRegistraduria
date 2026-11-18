"""
Pruebas white-box de la sesión: /api/auth/ingresar/, refrescar/, salir/ y sesion/.

Cada regla de seguridad de docs/decisiones/0002 tiene aquí al menos una prueba:
cookie HttpOnly y SameSite=Strict, token de refresco fuera del JSON, mismo error para
todo fallo de inicio de sesión, rotación con revocación y vencimiento conservado,
cabecera propia contra CSRF, límite de intentos y efecto inmediato de desactivar a un
usuario o quitarle el rol.
"""
from datetime import timedelta

import jwt
import pytest
from django.conf import settings
from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.cuentas.roles import ADMINISTRADOR, ANALISTA

from .conftest import CONTRASENA_PRUEBA

NOMBRE_COOKIE = settings.JWT_COOKIE['NOMBRE']
OCHO_HORAS = 8 * 60 * 60
CREDENCIALES_INVALIDAS = {'codigo': 'CREDENCIALES_INVALIDAS', 'mensaje': 'Usuario o contraseña incorrectos.'}
SESION_EXPIRADA = {'codigo': 'SESION_EXPIRADA', 'mensaje': 'Tu sesión terminó. Inicia sesión de nuevo.'}
SOLICITUD_RECHAZADA = {'codigo': 'SOLICITUD_RECHAZADA', 'mensaje': 'La solicitud no proviene de la aplicación.'}
NO_AUTENTICADO = {'codigo': 'NO_AUTENTICADO', 'mensaje': 'Inicia sesión para continuar.'}
TOKEN_INVALIDO = {'codigo': 'TOKEN_INVALIDO', 'mensaje': 'Tu sesión no es válida o venció. Inicia sesión de nuevo.'}
SIN_PERMISO = {'codigo': 'SIN_PERMISO', 'mensaje': 'No tienes permiso para realizar esta acción.'}


@pytest.fixture
def analista(crear_usuario):
    """Analista activo, el usuario por defecto de ingresar()."""
    return crear_usuario()


@pytest.fixture
def refrescar(cliente, cabecera_app):
    """Función que llama a /api/auth/refrescar/ con la cabecera de la aplicación (o sin ella)."""
    def _refrescar(con_cabecera=True):
        """POST sin cuerpo; el cliente envía la cookie que tenga guardada."""
        return cliente.post(reverse('cuentas:refrescar'), **(cabecera_app if con_cabecera else {}))
    return _refrescar


@pytest.fixture
def salir(cliente, cabecera_app):
    """Función que llama a /api/auth/salir/ con la cabecera de la aplicación."""
    return lambda: cliente.post(reverse('cuentas:salir'), **cabecera_app)


@pytest.fixture
def ver_sesion(cliente):
    """Función que llama a /api/auth/sesion/ con el token de acceso indicado (o sin token)."""
    def _ver_sesion(acceso=None):
        """GET con la cabecera Authorization: Bearer <acceso>, si se indica."""
        cabeceras = {'HTTP_AUTHORIZATION': f'Bearer {acceso}'} if acceso is not None else {}
        return cliente.get(reverse('cuentas:sesion'), **cabeceras)
    return _ver_sesion


def cookie(respuesta):
    """La cookie del token de refresco que puso la respuesta (un Morsel con sus atributos)."""
    return respuesta.cookies[NOMBRE_COOKIE]


# --- Iniciar sesión -----------------------------------------------------------------------

@pytest.mark.parametrize('rol', [ADMINISTRADOR, ANALISTA])
def test_ingresar_devuelve_el_token_de_acceso_y_el_usuario(crear_usuario, ingresar, rol):
    crear_usuario(rol=rol)

    respuesta = ingresar()

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {'acceso', 'tipo', 'expira_en', 'usuario'}
    assert cuerpo['tipo'] == 'Bearer'
    assert cuerpo['expira_en'] == 15 * 60
    assert cuerpo['usuario'] == {'usuario': 'usuario.prueba', 'nombre': 'Usuario Prueba', 'rol': rol}
    assert AccessToken(cuerpo['acceso'])['token_type'] == 'access'


def test_el_token_de_refresco_va_solo_en_la_cookie(analista, ingresar):
    respuesta = ingresar()

    refresco = cookie(respuesta).value
    assert RefreshToken(refresco)['token_type'] == 'refresh'
    assert refresco not in respuesta.content.decode()
    assert 'refresh' not in respuesta.json()


def test_atributos_de_seguridad_de_la_cookie(analista, ingresar):
    galleta = cookie(ingresar())

    assert galleta['httponly'] is True
    assert galleta['samesite'] == 'Strict'
    assert galleta['path'] == '/api/auth/'
    assert 0 < galleta['max-age'] <= OCHO_HORAS
    assert not galleta['secure']


def test_cookie_secure_cuando_se_activa_jwt_cookie_secure(analista, ingresar):
    with override_settings(JWT_COOKIE={**settings.JWT_COOKIE, 'SECURE': True}):
        galleta = cookie(ingresar())

    assert galleta['secure'] is True


def test_el_usuario_se_escribe_con_espacios_externos(analista, ingresar):
    assert ingresar('  usuario.prueba  ').status_code == 200


@pytest.mark.parametrize('caso', ['usuario_inexistente', 'contrasena_incorrecta', 'desactivado', 'sin_rol', 'superusuario'])
def test_todo_fallo_de_inicio_de_sesion_da_el_mismo_error(crear_usuario, ingresar, caso):
    """Así nadie puede averiguar qué usuarios existen ni si acertó la contraseña de una cuenta sin acceso."""
    usuario, contrasena = 'usuario.prueba', CONTRASENA_PRUEBA
    if caso == 'usuario_inexistente':
        usuario = 'no.existe'
    elif caso == 'contrasena_incorrecta':
        crear_usuario()
        contrasena = 'Otra-Clave-2026'
    elif caso == 'desactivado':
        crear_usuario(activo=False)
    elif caso == 'sin_rol':
        crear_usuario(rol=None)
    else:
        crear_usuario(rol=ADMINISTRADOR, superusuario=True, staff=True)

    respuesta = ingresar(usuario, contrasena)

    assert respuesta.status_code == 401
    assert respuesta.json() == CREDENCIALES_INVALIDAS
    assert respuesta['WWW-Authenticate'] == 'Bearer realm="api"'
    assert NOMBRE_COOKIE not in respuesta.cookies


@pytest.mark.parametrize('cuerpo', [
    {}, {'usuario': 'usuario.prueba'}, {'contrasena': CONTRASENA_PRUEBA}, {'usuario': '', 'contrasena': ''},
    {'usuario': '   ', 'contrasena': CONTRASENA_PRUEBA}, {'usuario': None, 'contrasena': None},
    {'usuario': 123, 'contrasena': CONTRASENA_PRUEBA},
], ids=['vacio', 'sin_contrasena', 'sin_usuario', 'textos_vacios', 'usuario_espacios', 'nulos', 'usuario_numero'])
def test_ingresar_sin_datos_completos(cliente, cuerpo):
    respuesta = cliente.post(reverse('cuentas:ingresar'), cuerpo, format='json')

    assert respuesta.status_code == 400
    assert respuesta.json() == {'codigo': 'DATOS_INCOMPLETOS', 'mensaje': 'Escribe tu usuario y tu contraseña.'}


def test_ingresar_con_json_que_no_es_objeto(cliente):
    respuesta = cliente.post(reverse('cuentas:ingresar'), '["usuario"]', content_type='application/json')

    assert respuesta.status_code == 400
    assert respuesta.json()['codigo'] == 'SOLICITUD_INVALIDA'


def test_ingresar_con_un_formulario_en_lugar_de_json(cliente):
    respuesta = cliente.post(reverse('cuentas:ingresar'), {'usuario': 'a', 'contrasena': 'b'})

    assert respuesta.status_code == 415
    assert respuesta.json()['codigo'] == 'SOLICITUD_INVALIDA'


@pytest.mark.parametrize('nombre', ['ingresar', 'refrescar', 'salir'])
def test_rutas_de_sesion_solo_aceptan_post(cliente, nombre):
    respuesta = cliente.get(reverse(f'cuentas:{nombre}'))

    assert respuesta.status_code == 405
    assert respuesta.json() == {'codigo': 'METODO_NO_PERMITIDO', 'mensaje': 'Usa POST en esta ruta.'}
    assert 'POST' in respuesta['Allow']


def test_un_token_invalido_en_la_cabecera_no_impide_iniciar_sesion(analista, ingresar):
    assert ingresar(HTTP_AUTHORIZATION='Bearer basura').status_code == 200


# --- Límite de intentos -------------------------------------------------------------------

def test_sexto_intento_en_un_minuto_responde_429(analista, ingresar):
    for _ in range(5):
        assert ingresar(contrasena='Otra-Clave-2026').status_code == 401

    respuesta = ingresar()

    assert respuesta.status_code == 429
    assert respuesta.json() == {
        'codigo': 'DEMASIADOS_INTENTOS',
        'mensaje': 'Hiciste demasiados intentos. Espera un minuto e inténtalo de nuevo.',
    }
    assert 'Retry-After' in respuesta


def test_falsificar_x_forwarded_for_no_evade_el_limite(analista, ingresar):
    for numero in range(5):
        ingresar(contrasena='Otra-Clave-2026', HTTP_X_FORWARDED_FOR=f'10.0.0.{numero}')

    assert ingresar(HTTP_X_FORWARDED_FOR='10.0.0.99').status_code == 429


def test_el_limite_es_por_ip(analista, ingresar):
    for _ in range(5):
        ingresar(contrasena='Otra-Clave-2026', REMOTE_ADDR='10.0.0.1')

    assert ingresar(REMOTE_ADDR='10.0.0.2').status_code == 200


# --- Renovar la sesión --------------------------------------------------------------------

def test_refrescar_entrega_un_token_de_acceso_nuevo_y_rota_la_cookie(analista, ingresar, refrescar):
    original = cookie(ingresar()).value

    respuesta = refrescar()

    assert respuesta.status_code == 200
    assert respuesta.json()['usuario']['rol'] == ANALISTA
    nueva = cookie(respuesta)
    assert nueva.value != original
    assert nueva['httponly'] is True
    assert nueva.value not in respuesta.content.decode()


def test_la_cookie_anterior_queda_revocada_tras_refrescar(analista, cliente, ingresar, refrescar):
    original = cookie(ingresar()).value
    refrescar()
    cliente.cookies[NOMBRE_COOKIE] = original

    respuesta = refrescar()

    assert respuesta.status_code == 401
    assert respuesta.json() == SESION_EXPIRADA


def test_refrescar_no_alarga_la_sesion_mas_alla_de_8_horas(analista, cliente, refrescar):
    """
    La rotación conserva el vencimiento del token original: la sesión no se renueva sin fin.

    El original vence en 1 hora (como si la sesión llevara 7). Si la rotación renovara el
    vencimiento, el nuevo volvería a durar 8 horas. Con tokens recién creados no se notaría:
    los dos vencerían en el mismo segundo.
    """
    original = RefreshToken.for_user(analista)
    original.set_exp(lifetime=timedelta(hours=1))
    cliente.cookies[NOMBRE_COOKIE] = str(original)

    respuesta = refrescar()

    renovado = RefreshToken(cookie(respuesta).value)
    assert renovado['exp'] == original['exp']
    assert renovado['jti'] != original['jti']
    assert cookie(respuesta)['max-age'] <= 60 * 60


def test_refrescar_sin_cookie(analista, refrescar):
    respuesta = refrescar()

    assert respuesta.status_code == 401
    assert respuesta.json() == SESION_EXPIRADA


def test_refrescar_con_cookie_vencida(analista, cliente, refrescar):
    vencido = RefreshToken.for_user(analista)
    vencido.set_exp(lifetime=timedelta(seconds=-1))
    cliente.cookies[NOMBRE_COOKIE] = str(vencido)

    assert refrescar().json() == SESION_EXPIRADA


def test_refrescar_con_un_token_de_acceso_en_la_cookie(analista, cliente, refrescar):
    cliente.cookies[NOMBRE_COOKIE] = str(AccessToken.for_user(analista))

    assert refrescar().json() == SESION_EXPIRADA


@pytest.mark.parametrize('cambio', ['desactivado', 'sin_rol', 'borrado'])
def test_refrescar_cuando_el_usuario_perdio_el_acceso(analista, ingresar, refrescar, cambio):
    """Un usuario borrado no debe causar un error 500: la sesión simplemente termina."""
    ingresar()
    if cambio == 'desactivado':
        analista.is_active = False
        analista.save()
    elif cambio == 'sin_rol':
        analista.groups.clear()
    else:
        analista.delete()

    respuesta = refrescar()

    assert respuesta.status_code == 401
    assert respuesta.json() == SESION_EXPIRADA


@pytest.mark.parametrize('cabecera', [None, 'XMLHttpRequest'], ids=['sin_cabecera', 'valor_distinto'])
def test_refrescar_exige_la_cabecera_de_la_aplicacion(analista, cliente, ingresar, cabecera):
    """Protección contra CSRF: una página de otro sitio no puede agregar esta cabecera."""
    ingresar()
    extra = {'HTTP_X_REQUESTED_WITH': cabecera} if cabecera else {}

    respuesta = cliente.post(reverse('cuentas:refrescar'), **extra)

    assert respuesta.status_code == 403
    assert respuesta.json() == SOLICITUD_RECHAZADA


# --- Cerrar sesión ------------------------------------------------------------------------

def test_salir_revoca_la_cookie_y_la_borra(analista, cliente, ingresar, salir, refrescar):
    original = cookie(ingresar()).value

    respuesta = salir()

    assert respuesta.status_code == 204
    assert cookie(respuesta).value == ''
    assert cookie(respuesta)['max-age'] == 0
    cliente.cookies[NOMBRE_COOKIE] = original
    assert refrescar().json() == SESION_EXPIRADA


def test_salir_sin_sesion_tambien_responde_204(salir):
    assert salir().status_code == 204


def test_salir_exige_la_cabecera_de_la_aplicacion(analista, cliente, ingresar, refrescar):
    ingresar()

    respuesta = cliente.post(reverse('cuentas:salir'))

    assert respuesta.status_code == 403
    assert respuesta.json() == SOLICITUD_RECHAZADA
    assert refrescar().status_code == 200


# --- Usuario de la sesión y token de acceso ------------------------------------------------

@pytest.mark.parametrize('rol', [ADMINISTRADOR, ANALISTA])
def test_sesion_devuelve_el_usuario_y_su_rol(crear_usuario, ingresar, ver_sesion, rol):
    crear_usuario(rol=rol)

    respuesta = ver_sesion(ingresar().json()['acceso'])

    assert respuesta.status_code == 200
    assert respuesta.json() == {'usuario': 'usuario.prueba', 'nombre': 'Usuario Prueba', 'rol': rol}


def test_sesion_sin_token(ver_sesion):
    respuesta = ver_sesion()

    assert respuesta.status_code == 401
    assert respuesta.json() == NO_AUTENTICADO
    assert respuesta['WWW-Authenticate'] == 'Bearer realm="api"'


def test_sesion_solo_acepta_get(analista, cliente, ingresar):
    """Con token: DRF revisa la autenticación antes que el método, así que sin token sería un 401."""
    acceso = ingresar().json()['acceso']

    respuesta = cliente.post(reverse('cuentas:sesion'), HTTP_AUTHORIZATION=f'Bearer {acceso}')

    assert respuesta.status_code == 405
    assert respuesta.json() == {'codigo': 'METODO_NO_PERMITIDO', 'mensaje': 'Usa GET en esta ruta.'}


def _token_falsificado(analista, como):
    """Token de acceso alterado de distintas formas, todas inválidas."""
    valido = AccessToken.for_user(analista)
    if como == 'vencido':
        valido.set_exp(lifetime=timedelta(seconds=-1))
        return str(valido)
    if como == 'firma_alterada':
        texto = str(valido)
        return texto[:-2] + ('AA' if not texto.endswith('AA') else 'BB')
    if como == 'otra_clave':
        return jwt.encode(dict(valido.payload), 'una-clave-que-no-es-la-del-servidor', algorithm='HS256')
    if como == 'alg_none':
        return jwt.encode(dict(valido.payload), None, algorithm='none')
    if como == 'token_de_refresco':
        return str(RefreshToken.for_user(analista))
    return 'esto-no-es-un-jwt'


@pytest.mark.parametrize('como', ['vencido', 'firma_alterada', 'otra_clave', 'alg_none', 'token_de_refresco', 'basura'])
def test_token_de_acceso_invalido(analista, ver_sesion, como):
    respuesta = ver_sesion(_token_falsificado(analista, como))

    assert respuesta.status_code == 401
    assert respuesta.json() == TOKEN_INVALIDO


def test_desactivar_al_usuario_le_quita_el_acceso_de_inmediato(analista, ingresar, ver_sesion):
    acceso = ingresar().json()['acceso']
    analista.is_active = False
    analista.save()

    respuesta = ver_sesion(acceso)

    assert respuesta.status_code == 401
    assert respuesta.json() == TOKEN_INVALIDO


def test_quitar_el_rol_le_quita_el_acceso_de_inmediato(analista, ingresar, ver_sesion):
    """El rol se lee de la base en cada petición, no del token (que sigue vigente)."""
    acceso = ingresar().json()['acceso']
    analista.groups.clear()

    respuesta = ver_sesion(acceso)

    assert respuesta.status_code == 403
    assert respuesta.json() == SIN_PERMISO


def test_cambiar_el_rol_se_refleja_sin_volver_a_iniciar_sesion(analista, ingresar, ver_sesion):
    acceso = ingresar().json()['acceso']
    analista.groups.set([Group.objects.get(name=ADMINISTRADOR)])

    assert ver_sesion(acceso).json()['rol'] == ADMINISTRADOR


def test_el_token_de_acceso_no_lleva_el_rol(analista, ingresar):
    """Si el rol fuera en el token, quitarlo no tendría efecto hasta que el token venciera."""
    carga = AccessToken(ingresar().json()['acceso']).payload

    assert 'rol' not in carga
    assert 'groups' not in carga


# --- La consulta electoral sigue siendo pública ----------------------------------------------

def test_la_consulta_publica_ignora_un_token_invalido(consultar):
    respuesta = consultar('1098765432', HTTP_AUTHORIZATION='Bearer basura')

    assert respuesta.status_code == 200
