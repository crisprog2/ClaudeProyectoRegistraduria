"""Steps del feature validaciones_cedula.feature (ejecutados en el navegador)."""
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from support.data_loader import caso

pytestmark = pytest.mark.e2e

scenarios('validaciones_cedula.feature')


@given('una cédula con formato válido que no está registrada', target_fixture='cedula_no_registrada')
def cedula_no_registrada():
    """Cédula del caso 'no_registrada' de tests/data/cedulas_invalidas.json."""
    return caso('cedulas_invalidas', 'no_registrada')['cuerpo']['cedula']


@when('consulta sin escribir el número de cédula')
def consultar_sin_cedula(consulta):
    """Pulsa Consultar con el campo vacío."""
    consulta.abrir()
    consulta.enviar()


@when(parsers.parse('consulta con la cédula "{cedula}"'))
def consultar_con_cedula(consulta, cedula):
    """Consulta con la cédula escrita en el escenario (ejemplos del esquema)."""
    consulta.abrir()
    consulta.consultar(cedula)


@when('consulta con esa cédula')
def consultar_con_esa_cedula(consulta, cedula_no_registrada):
    """Consulta con la cédula elegida en el paso Dado."""
    consulta.abrir()
    consulta.consultar(cedula_no_registrada)


@then('no ve información de votación')
def no_ve_informacion(consulta, resultado):
    """Sigue en la pantalla de consulta, sin ninguna sección del resultado."""
    assert consulta.ruta_actual() == consulta.RUTA
    expect(resultado.resumen).to_have_count(0)
    expect(resultado.tarjeta_votacion).to_have_count(0)
    expect(resultado.tarjeta_jurado).to_have_count(0)
