"""
Pruebas white-box del manejador central de errores (exceptions.manejador_de_errores).

Los errores que produce la API real ya se prueban de punta a punta en
test_api_consulta.py. Aquí se prueban los dos caminos que la API de consulta no
alcanza hoy: un error no controlado y un error de DRF sin código propio.
"""
from django.http import Http404
from rest_framework import exceptions, status

from apps.consultas.exceptions import manejador_de_errores


def test_error_no_controlado_queda_para_django():
    """Devolver None hace que Django responda 500 sin exponer el detalle del error."""
    assert manejador_de_errores(RuntimeError('detalle interno'), {}) is None


def test_error_de_drf_sin_codigo_propio_conserva_el_formato():
    """
    Un error de DRF que no está en ERRORES_DRF sale como ERROR_DE_SOLICITUD con el texto de DRF.

    Por ejemplo, el 401 que aparecerá si un endpoint exige autenticación: conserva
    su código HTTP y el cuerpo sigue siendo {codigo, mensaje}.
    """
    respuesta = manejador_de_errores(exceptions.NotAuthenticated(), {})

    assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED
    assert respuesta.data == {
        'codigo': 'ERROR_DE_SOLICITUD',
        'mensaje': str(exceptions.NotAuthenticated.default_detail),
    }


def test_404_de_django_conserva_el_formato():
    respuesta = manejador_de_errores(Http404(), {})

    assert respuesta.status_code == status.HTTP_404_NOT_FOUND
    assert set(respuesta.data) == {'codigo', 'mensaje'}
