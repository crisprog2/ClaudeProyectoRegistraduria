"""Steps del feature consulta_jurado.feature (ejecutados en el navegador)."""
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then

from support.data_loader import caso

pytestmark = pytest.mark.e2e

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
def ve_su_designacion(resultado, rol):
    """Están el aviso de jurado y la tarjeta de asignación con el rol indicado."""
    expect(resultado.aviso_jurado).to_be_visible()
    expect(resultado.tarjeta_jurado).to_contain_text(rol)


@then('su mesa de servicio es la misma donde vota')
def misma_mesa(resultado):
    """La mesa, el puesto y la dirección de las dos tarjetas coinciden."""
    assert resultado.numero_de_mesa(resultado.tarjeta_jurado) == resultado.numero_de_mesa(resultado.tarjeta_votacion)
    puesto_voto = resultado.valor_de(resultado.tarjeta_votacion, 'Puesto de votación').inner_text()
    direccion_voto = resultado.valor_de(resultado.tarjeta_votacion, 'Dirección').inner_text()
    expect(resultado.valor_de(resultado.tarjeta_jurado, 'Puesto de servicio como jurado')).to_have_text(puesto_voto)
    expect(resultado.valor_de(resultado.tarjeta_jurado, 'Dirección de servicio')).to_have_text(direccion_voto)


@then('su mesa de servicio es distinta a la mesa donde vota')
def otra_mesa(resultado):
    """Las dos tarjetas muestran mesas diferentes."""
    assert resultado.numero_de_mesa(resultado.tarjeta_jurado) != resultado.numero_de_mesa(resultado.tarjeta_votacion)


@then('su puesto de servicio es el mismo donde vota')
def mismo_puesto(resultado):
    """El puesto de servicio coincide con el de votación."""
    puesto_voto = resultado.valor_de(resultado.tarjeta_votacion, 'Puesto de votación').inner_text()
    expect(resultado.valor_de(resultado.tarjeta_jurado, 'Puesto de servicio como jurado')).to_have_text(puesto_voto)


@then('su puesto y su dirección de servicio son distintos a los de votación')
def otro_puesto(resultado):
    """El jurado presta servicio en un puesto y una dirección diferentes a los de votación."""
    puesto_voto = resultado.valor_de(resultado.tarjeta_votacion, 'Puesto de votación').inner_text()
    direccion_voto = resultado.valor_de(resultado.tarjeta_votacion, 'Dirección').inner_text()
    expect(resultado.valor_de(resultado.tarjeta_jurado, 'Puesto de servicio como jurado')).not_to_have_text(puesto_voto)
    expect(resultado.valor_de(resultado.tarjeta_jurado, 'Dirección de servicio')).not_to_have_text(direccion_voto)
