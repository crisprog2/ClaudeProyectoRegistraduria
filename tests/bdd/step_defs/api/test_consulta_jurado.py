"""Steps del feature consulta_jurado.feature (ejecutados contra la API)."""
import pytest
from pytest_bdd import given, parsers, scenarios, then

from support.data_loader import caso

pytestmark = pytest.mark.api

scenarios('consulta_jurado.feature')


@given('un ciudadano designado jurado titular en la misma mesa donde vota', target_fixture='ciudadano')
def jurado_misma_mesa():
    """Caso 'jurado_misma_mesa' de tests/data/ciudadanos.json."""
    return caso('ciudadanos', 'jurado_misma_mesa')


@given('un ciudadano designado jurado remanente en otra mesa del mismo puesto', target_fixture='ciudadano')
def jurado_otra_mesa_mismo_puesto():
    """Caso 'jurado_otra_mesa_mismo_puesto' de tests/data/ciudadanos.json."""
    return caso('ciudadanos', 'jurado_otra_mesa_mismo_puesto')


@given('un ciudadano designado jurado titular en otro puesto de votación', target_fixture='ciudadano')
def jurado_otro_puesto():
    """Caso 'jurado_otro_puesto' de tests/data/ciudadanos.json."""
    return caso('ciudadanos', 'jurado_otro_puesto')


@then(parsers.parse('ve su designación como "{rol}"'))
def ve_su_designacion(respuesta, rol):
    """La designación existe y su rol visible es el indicado."""
    assert respuesta.status_code == 200
    jurado = respuesta.json()['jurado']
    assert jurado is not None
    assert jurado['rol_display'] == rol


@then('su mesa de servicio es la misma donde vota')
def misma_mesa(respuesta):
    """Mesa, puesto y dirección de servicio iguales a los de votación."""
    cuerpo = respuesta.json()
    jurado, lugar = cuerpo['jurado'], cuerpo['lugar_votacion']
    assert jurado['misma_mesa'] is True
    assert {clave: jurado[clave] for clave in lugar} == lugar


@then('su mesa de servicio es distinta a la mesa donde vota')
def otra_mesa(respuesta):
    """La mesa de servicio no es la mesa de votación."""
    cuerpo = respuesta.json()
    assert cuerpo['jurado']['misma_mesa'] is False
    assert cuerpo['jurado']['mesa'] != cuerpo['lugar_votacion']['mesa']


@then('su puesto de servicio es el mismo donde vota')
def mismo_puesto(respuesta):
    """El puesto de servicio coincide con el de votación."""
    cuerpo = respuesta.json()
    assert cuerpo['jurado']['puesto'] == cuerpo['lugar_votacion']['puesto']


@then('su puesto y su dirección de servicio son distintos a los de votación')
def otro_puesto(respuesta):
    """El jurado presta servicio en un puesto diferente al de votación."""
    cuerpo = respuesta.json()
    jurado, lugar = cuerpo['jurado'], cuerpo['lugar_votacion']
    assert jurado['misma_mesa'] is False
    assert jurado['puesto'] != lugar['puesto']
    assert jurado['direccion'] != lugar['direccion']
