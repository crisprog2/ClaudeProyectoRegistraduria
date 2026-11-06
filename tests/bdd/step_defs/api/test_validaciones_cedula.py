"""Steps del feature validaciones_cedula.feature (ejecutados contra la API)."""
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from support.data_loader import caso

pytestmark = pytest.mark.api

scenarios('validaciones_cedula.feature')


@given('una cédula con formato válido que no está registrada', target_fixture='cedula_no_registrada')
def cedula_no_registrada():
    """Cédula del caso 'no_registrada' de tests/data/cedulas_invalidas.json."""
    return caso('cedulas_invalidas', 'no_registrada')['cuerpo']['cedula']


@when('consulta sin escribir el número de cédula', target_fixture='respuesta')
def consultar_sin_cedula(api):
    """Consulta con el campo vacío."""
    return api.consultar('')


@when(parsers.parse('consulta con la cédula "{cedula}"'), target_fixture='respuesta')
def consultar_con_cedula(api, cedula):
    """Consulta con la cédula escrita en el escenario (ejemplos del esquema)."""
    return api.consultar(cedula)


@when('consulta con esa cédula', target_fixture='respuesta')
def consultar_con_esa_cedula(api, cedula_no_registrada):
    """Consulta con la cédula elegida en el paso Dado."""
    return api.consultar(cedula_no_registrada)


@then('no ve información de votación')
def no_ve_informacion(respuesta):
    """La respuesta de error no incluye datos del ciudadano, del lugar de votación ni de jurado."""
    assert not {'ciudadano', 'lugar_votacion', 'jurado'} & set(respuesta.json())
