"""
Pruebas white-box del manejador central de errores (exceptions.manejador_de_errores).

Los errores que produce la API real ya se prueban de punta a punta en
test_api_consulta.py y test_autenticacion.py. Aquí se prueban los caminos del
manejador que esas rutas no alcanzan, y el orden en que elige el código de un error.
"""
from django.http import Http404
from rest_framework import exceptions, status

from apps.consultas.exceptions import manejador_de_errores
from apps.cuentas.excepciones import CredencialesInvalidas


class VistaConTextosPropios:
    """Vista falsa con su propio texto para el 405, como las de apps/cuentas."""
    errores_drf = {exceptions.MethodNotAllowed: ('METODO_NO_PERMITIDO', 'Usa GET en esta ruta.')}


def test_error_no_controlado_queda_para_django():
    """Devolver None hace que Django responda 500 sin exponer el detalle del error."""
    assert manejador_de_errores(RuntimeError('detalle interno'), {}) is None


def test_error_de_drf_sin_codigo_propio_conserva_el_formato():
    """Un error de DRF que nadie traduce sale como ERROR_DE_SOLICITUD, con su código HTTP y el texto de DRF."""
    respuesta = manejador_de_errores(exceptions.NotAcceptable(), {})

    assert respuesta.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert respuesta.data == {'codigo': 'ERROR_DE_SOLICITUD', 'mensaje': str(exceptions.NotAcceptable.default_detail)}


def test_404_de_django_conserva_el_formato():
    respuesta = manejador_de_errores(Http404(), {})

    assert respuesta.status_code == status.HTTP_404_NOT_FOUND
    assert set(respuesta.data) == {'codigo', 'mensaje'}


def test_una_excepcion_con_codigo_propio_usa_su_codigo_y_su_cabecera():
    respuesta = manejador_de_errores(CredencialesInvalidas(), {})

    assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED
    assert respuesta.data == {'codigo': 'CREDENCIALES_INVALIDAS', 'mensaje': 'Usuario o contraseña incorrectos.'}
    assert respuesta['WWW-Authenticate'] == 'Bearer realm="api"'


def test_los_textos_de_la_vista_tienen_prioridad_sobre_los_comunes():
    respuesta = manejador_de_errores(exceptions.MethodNotAllowed('POST'), {'view': VistaConTextosPropios()})

    assert respuesta.data == {'codigo': 'METODO_NO_PERMITIDO', 'mensaje': 'Usa GET en esta ruta.'}


def test_sin_textos_de_la_vista_se_usan_los_comunes():
    respuesta = manejador_de_errores(exceptions.MethodNotAllowed('GET'), {'view': object()})

    assert respuesta.data == {'codigo': 'METODO_NO_PERMITIDO', 'mensaje': 'Usa POST para consultar.'}
