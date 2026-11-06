"""
Pruebas E2E de casos de error: errores del campo, cédula no encontrada y fallas de la red.

Las fallas que no se pueden provocar a voluntad (429 y servidor caído) se simulan interceptando la petición.
"""
import pytest
from playwright.sync_api import expect

from support.data_loader import caso, cargar

pytestmark = pytest.mark.e2e

TEXTOS = cargar('textos_interfaz')
CEDULA_VALIDA = caso('ciudadanos', 'solo_votante')['cedula']
CEDULA_NO_REGISTRADA = caso('cedulas_invalidas', 'no_registrada')['cuerpo']['cedula']
ERRORES_DEL_CAMPO = TEXTOS['errores_del_campo']


@pytest.mark.parametrize('error', ERRORES_DEL_CAMPO, ids=lambda error: error['id'])
def test_error_del_campo_se_muestra_en_lugar_de_la_ayuda(consulta, mensajes_error, error):
    consulta.abrir()
    expect(consulta.ayuda).to_be_visible()

    consulta.consultar(error['valor'])

    expect(consulta.alerta).to_have_text(mensajes_error[error['codigo']])
    expect(consulta.ayuda).to_have_count(0)
    expect(consulta.campo).to_have_attribute('aria-invalid', 'true')
    expect(consulta.campo).to_be_focused()


@pytest.mark.parametrize('error', ERRORES_DEL_CAMPO, ids=lambda error: error['id'])
def test_error_del_campo_no_llama_a_la_api(consulta, peticiones_api, error):
    consulta.abrir()
    consulta.consultar(error['valor'])
    consulta.alerta.wait_for()
    assert peticiones_api == []


def test_cedula_no_encontrada_muestra_el_panel_con_el_campo_normal(consulta):
    panel = TEXTOS['panel_sin_resultado']['no_encontrada']
    consulta.abrir()
    consulta.consultar(CEDULA_NO_REGISTRADA)

    expect(consulta.alerta).to_contain_text(panel['titulo'])
    expect(consulta.alerta).to_contain_text(panel['detalle'])
    expect(consulta.ayuda).to_have_count(0)
    expect(consulta.campo).to_have_attribute('aria-invalid', 'false')


def test_al_editar_el_campo_desaparece_el_error(consulta):
    consulta.abrir()
    consulta.enviar()
    consulta.alerta.wait_for()

    consulta.escribir('1')

    expect(consulta.alerta).to_have_count(0)
    expect(consulta.ayuda).to_be_visible()
    expect(consulta.campo).to_have_attribute('aria-invalid', 'false')


def test_despues_de_un_error_se_puede_consultar_de_nuevo(consulta, resultado):
    consulta.abrir()
    consulta.consultar(CEDULA_NO_REGISTRADA)
    consulta.alerta.wait_for()

    consulta.consultar(CEDULA_VALIDA)
    consulta.page.wait_for_url(f'**{resultado.RUTA}')

    expect(resultado.resumen).to_be_visible()


def test_demasiadas_consultas_muestra_su_mensaje(consulta, mensajes_error, page):
    panel = TEXTOS['panel_sin_resultado']['demasiadas_consultas']
    page.route('**/api/consulta/', lambda ruta: ruta.fulfill(
        status=429,
        headers={'Retry-After': '30'},
        json={'codigo': 'DEMASIADAS_CONSULTAS', 'mensaje': mensajes_error['DEMASIADAS_CONSULTAS']},
    ))
    consulta.abrir()
    consulta.consultar(CEDULA_VALIDA)

    expect(consulta.alerta).to_contain_text(panel['titulo'])
    expect(consulta.alerta).to_contain_text(panel['detalle'])


@pytest.mark.parametrize('falla', ['conexion_caida', 'error_500_sin_json'])
def test_falla_del_servicio_muestra_el_mensaje_generico(consulta, page, falla):
    panel = TEXTOS['panel_sin_resultado']['falla']
    if falla == 'conexion_caida':
        page.route('**/api/consulta/', lambda ruta: ruta.abort())
    else:
        page.route('**/api/consulta/', lambda ruta: ruta.fulfill(status=500, body='Error interno'))
    consulta.abrir()
    consulta.consultar(CEDULA_VALIDA)

    expect(consulta.alerta).to_contain_text(panel['titulo'])
    expect(consulta.alerta).to_contain_text(panel['detalle'])
    expect(consulta.boton).to_be_enabled()
    assert consulta.ruta_actual() == consulta.RUTA
