"""
Pruebas E2E de accesibilidad: auditoría con axe-core y manejo del foco y de los títulos.

axe solo detecta una parte de los problemas: estas pruebas no reemplazan una revisión con lector de pantalla.
"""
import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import expect

from support.data_loader import caso, cargar, como_parametros

pytestmark = pytest.mark.e2e

TEXTOS = cargar('textos_interfaz')
CEDULA_VOTANTE = caso('ciudadanos', 'solo_votante')['cedula']
REGLAS_AXE = {'runOnly': ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice']}


@pytest.mark.parametrize('pantalla', como_parametros('pantallas'))
def test_pantalla_sin_violaciones_de_axe(page, abrir_pantalla, pantalla):
    abrir_pantalla(pantalla)

    resultados = Axe().run(page, options=REGLAS_AXE)

    violaciones = [
        f"{violacion['id']} ({violacion['impact']}): {[nodo['target'] for nodo in violacion['nodes']]}"
        for violacion in resultados.response['violations']
    ]
    assert violaciones == []


def test_titulo_de_la_pestana_cambia_con_la_pantalla(consulta, page):
    titulos = TEXTOS['titulos_pestana']
    consulta.abrir()
    expect(page).to_have_title(titulos['consulta'])
    consulta.consultar_hasta_resultado(CEDULA_VOTANTE)
    expect(page).to_have_title(titulos['resultado'])
    consulta.abrir(TEXTOS['ruta_inexistente'])
    expect(page).to_have_title(titulos['no_encontrada'])


def test_foco_pasa_al_titulo_al_llegar_al_resultado(consulta, resultado):
    consulta.consultar_hasta_resultado(CEDULA_VOTANTE)
    expect(resultado.titulo).to_be_focused()


def test_foco_pasa_al_titulo_al_volver_a_la_consulta(consulta, resultado):
    consulta.consultar_hasta_resultado(CEDULA_VOTANTE)
    resultado.otra_consulta.click()
    expect(consulta.campo).to_be_visible()
    expect(consulta.titulo).to_be_focused()


def test_saltar_al_contenido_mueve_el_foco_sin_perder_el_resultado(consulta, resultado, page):
    """El salto no debe tocar la URL: un cambio de hash borraría el estado de navegación."""
    consulta.consultar_hasta_resultado(CEDULA_VOTANTE)

    resultado.saltar.focus()
    expect(resultado.saltar).to_be_in_viewport()
    page.keyboard.press('Enter')

    expect(resultado.principal).to_be_focused()
    expect(resultado.resumen).to_be_visible()
    assert resultado.ruta_actual() == resultado.RUTA
