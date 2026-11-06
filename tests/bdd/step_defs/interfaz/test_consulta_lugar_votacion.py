"""Steps del feature consulta_lugar_votacion.feature (ejecutados en el navegador)."""
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, scenarios, then, when

from support.data_loader import caso
from support.edad import edad_esperada

pytestmark = pytest.mark.e2e

scenarios('consulta_lugar_votacion.feature')


@given('un ciudadano registrado que no fue designado jurado', target_fixture='ciudadano')
def ciudadano_solo_votante():
    """Caso 'solo_votante' de tests/data/ciudadanos.json."""
    return caso('ciudadanos', 'solo_votante')


@when('consulta con su número de cédula rodeado de espacios')
def consultar_con_espacios(consulta, ciudadano):
    """Consulta con la cédula precedida y seguida de espacios."""
    consulta.consultar_hasta_resultado(f"  {ciudadano['cedula']}  ")


@then('ve su nombre completo y su edad')
def ve_nombre_y_edad(resultado, ciudadano):
    """Nombre completo exacto y edad calculada con el oráculo de las pruebas."""
    expect(resultado.resumen).to_contain_text(ciudadano['esperado']['ciudadano']['nombre_completo'])
    expect(resultado.edad).to_have_text(f"Edad · {edad_esperada(ciudadano['fecha_nacimiento'])} años")


@then('se le informa que no tiene designación como jurado')
def no_tiene_designacion(resultado):
    """Está el aviso de votante y no está ninguna sección de jurado."""
    expect(resultado.aviso_votante).to_be_visible()
    expect(resultado.aviso_jurado).to_have_count(0)
    expect(resultado.tarjeta_jurado).to_have_count(0)
