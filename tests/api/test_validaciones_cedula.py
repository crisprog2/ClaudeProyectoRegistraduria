"""
Pruebas black-box de las validaciones de la cédula: vacía, formato inválido y no encontrada.

Los casos vienen de tests/data/cedulas_invalidas.json y los mensajes de
tests/data/mensajes_error.json (textos del Figma).
"""
import pytest

from support.data_loader import como_parametros

pytestmark = pytest.mark.api


@pytest.mark.parametrize('caso', como_parametros('cedulas_invalidas'))
def test_cedula_invalida_responde_codigo_y_mensaje(api, mensajes_error, caso):
    respuesta = api.enviar_json(caso['cuerpo'])

    assert respuesta.status_code == caso['http']
    assert respuesta.headers['Content-Type'].startswith('application/json')
    assert respuesta.json() == {'codigo': caso['codigo'], 'mensaje': mensajes_error[caso['codigo']]}
