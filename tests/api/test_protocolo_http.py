"""
Pruebas black-box del protocolo HTTP: métodos no permitidos y cuerpos que no son un objeto JSON.

Los casos vienen de tests/data/solicitudes_invalidas.json.
"""
import pytest

from support.data_loader import como_parametros

pytestmark = pytest.mark.api


@pytest.mark.parametrize('solicitud', como_parametros('solicitudes_invalidas'))
def test_solicitud_invalida_responde_codigo_y_mensaje(api, mensajes_error, solicitud):
    respuesta = api.enviar_solicitud(solicitud)

    assert respuesta.status_code == solicitud['http']
    assert respuesta.headers['Content-Type'].startswith('application/json')
    assert respuesta.json() == {'codigo': solicitud['codigo'], 'mensaje': mensajes_error[solicitud['codigo']]}


@pytest.mark.parametrize('solicitud', [
    parametro for parametro in como_parametros('solicitudes_invalidas') if parametro.values[0]['http'] == 405
])
def test_metodo_no_permitido_indica_que_se_usa_post(api, solicitud):
    """Un 405 debe incluir la cabecera Allow con POST, como exige HTTP."""
    respuesta = api.enviar_solicitud(solicitud)

    permitidos = {metodo.strip() for metodo in respuesta.headers['Allow'].split(',')}
    assert 'POST' in permitidos
    assert solicitud['metodo'] not in permitidos
