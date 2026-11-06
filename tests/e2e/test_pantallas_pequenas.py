"""Pruebas E2E de pantallas pequeñas: sin desborde horizontal y con los avisos visibles en cada ancho."""
import pytest
from playwright.sync_api import expect

from support.data_loader import cargar, como_parametros

pytestmark = pytest.mark.e2e

ANCHOS = cargar('textos_interfaz')['anchos_de_pantalla']


@pytest.mark.parametrize('ancho', ANCHOS)
@pytest.mark.parametrize('pantalla', como_parametros('pantallas'))
def test_sin_desborde_horizontal(consulta, page, abrir_pantalla, pantalla, ancho):
    page.set_viewport_size({'width': ancho, 'height': 900})
    abrir_pantalla(pantalla)
    assert consulta.desborde_horizontal() == 0
    expect(consulta.demo_banner.aviso).to_be_visible()
