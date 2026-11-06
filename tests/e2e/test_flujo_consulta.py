"""
Pruebas E2E del flujo de consulta: formato de los datos, navegación, privacidad y avisos obligatorios.

Las reglas de negocio de cada escenario están en los features de BDD; aquí se cubre lo que no describen.
"""
import pytest
from playwright.sync_api import expect

from support.data_loader import caso, cargar, como_parametros
from support.edad import edad_esperada

pytestmark = pytest.mark.e2e

TEXTOS = cargar('textos_interfaz')


def cedula_de(escenario):
    """Cédula del caso indicado de tests/data/ciudadanos.json."""
    return caso('ciudadanos', escenario)['cedula']


# Formato de los datos

@pytest.mark.parametrize('dato', TEXTOS['cedulas_formateadas'], ids=lambda dato: dato['id'])
def test_cedula_se_muestra_con_puntos(consulta, resultado, dato):
    consulta.consultar_hasta_resultado(cedula_de(dato['escenario']))
    expect(resultado.cedula).to_have_text(f"Cédula de ciudadanía · {dato['formateada']}")


def test_mesa_del_votante_tiene_tres_digitos(consulta, resultado):
    consulta.consultar_hasta_resultado(cedula_de('solo_votante'))
    assert resultado.numero_de_mesa(resultado.tarjeta_votacion) == '012'


def test_mesas_del_jurado_llevan_su_etiqueta(consulta, resultado):
    consulta.consultar_hasta_resultado(cedula_de('jurado_misma_mesa'))
    expect(resultado.tarjeta_votacion).to_contain_text('018 · Votación')
    expect(resultado.tarjeta_jurado).to_contain_text('018 · Jurado')


def test_votante_ve_su_edad(consulta, resultado):
    votante = caso('ciudadanos', 'solo_votante')
    consulta.consultar_hasta_resultado(votante['cedula'])
    expect(resultado.edad).to_have_text(f"Edad · {edad_esperada(votante['fecha_nacimiento'])} años")


def test_jurado_no_ve_su_edad(consulta, resultado):
    consulta.consultar_hasta_resultado(cedula_de('jurado_misma_mesa'))
    expect(resultado.resumen).to_be_visible()
    expect(resultado.edad).to_have_count(0)


# Contenido según la condición de la persona

def test_votante_ve_el_consejo_y_ninguna_seccion_de_jurado(consulta, resultado):
    consulta.consultar_hasta_resultado(cedula_de('solo_votante'))
    expect(resultado.aviso_votante).to_contain_text('VOTANTE')
    expect(resultado.consejo).to_be_visible()
    expect(resultado.aviso_jurado).to_have_count(0)
    expect(resultado.tarjeta_jurado).to_have_count(0)


@pytest.mark.parametrize('jurado', TEXTOS['jurados'], ids=lambda jurado: jurado['id'])
def test_textos_del_jurado_segun_donde_sirve(consulta, resultado, jurado):
    consulta.consultar_hasta_resultado(cedula_de(jurado['escenario']))
    expect(resultado.aviso_jurado).to_contain_text(jurado['aviso'])
    expect(resultado.aviso_jurado).to_contain_text('JURADO')
    expect(resultado.tarjeta_jurado).to_contain_text(jurado['detalle_tarjeta'])
    expect(resultado.mapa).to_contain_text(jurado['nota_mapa'])
    expect(resultado.notas).to_contain_text(jurado['titulo_nota'])
    expect(resultado.aviso_votante).to_have_count(0)
    expect(resultado.consejo).to_have_count(0)


# Mapa ilustrativo

def test_mapa_nombra_las_calles_solo_del_puesto_dibujado(consulta, resultado):
    mapa = TEXTOS['mapa']
    consulta.consultar_hasta_resultado(cedula_de(mapa['con_calles']))
    for calle in mapa['nombres_de_calles']:
        expect(resultado.plano).to_contain_text(calle)

    consulta.consultar_hasta_resultado(cedula_de(mapa['sin_calles']))
    expect(resultado.plano).to_be_visible()
    for calle in mapa['nombres_de_calles']:
        expect(resultado.plano).not_to_contain_text(calle)


def test_mapa_no_repite_ciudad_y_departamento_iguales(consulta, resultado):
    mapa = TEXTOS['mapa']
    consulta.consultar_hasta_resultado(cedula_de(mapa['sin_calles']))
    expect(resultado.mapa).to_contain_text(mapa['lugar_unico'])
    expect(resultado.mapa).not_to_contain_text(mapa['lugar_repetido'])


def test_mapa_se_declara_ilustrativo(consulta, resultado):
    consulta.consultar_hasta_resultado(cedula_de('solo_votante'))
    expect(resultado.mapa).to_contain_text('ILUSTRATIVO')
    expect(resultado.mapa).to_contain_text('no cartografía oficial')


# Navegación y privacidad

def test_cedula_nunca_viaja_en_la_url(consulta, page, peticiones_api):
    """Protege una regla de privacidad: la cédula no debe quedar en el historial ni en los logs."""
    cedula = cedula_de('solo_votante')
    direcciones = []
    page.on('framenavigated', lambda marco: direcciones.append(marco.url))

    consulta.consultar_hasta_resultado(cedula)

    assert direcciones, 'No se registró ninguna navegación'
    assert all(cedula not in direccion for direccion in direcciones)
    assert len(peticiones_api) == 1
    assert cedula not in peticiones_api[0].url
    assert cedula in peticiones_api[0].post_data


def test_raiz_redirige_a_la_consulta(consulta):
    consulta.abrir('/')
    assert consulta.ruta_actual() == consulta.RUTA


def test_recargar_el_resultado_vuelve_a_la_consulta(consulta, resultado, page):
    """El resultado con datos del ciudadano no debe sobrevivir a una recarga."""
    consulta.consultar_hasta_resultado(cedula_de('solo_votante'))
    page.reload()
    page.wait_for_url(f'**{consulta.RUTA}')
    expect(consulta.campo).to_be_visible()
    expect(resultado.resumen).to_have_count(0)


def test_entrar_directo_al_resultado_vuelve_a_la_consulta(consulta, resultado, page):
    page.goto(resultado.RUTA)
    page.wait_for_url(f'**{consulta.RUTA}')
    expect(consulta.campo).to_be_visible()


def test_realizar_otra_consulta_vuelve_con_el_campo_vacio(consulta, resultado, page):
    consulta.consultar_hasta_resultado(cedula_de('solo_votante'))
    resultado.otra_consulta.click()
    page.wait_for_url(f'**{consulta.RUTA}')
    expect(consulta.campo).to_have_value('')


def test_se_puede_consultar_de_nuevo_despues_de_recargar(consulta, resultado, page):
    consulta.consultar_hasta_resultado(cedula_de('solo_votante'))
    page.reload()
    page.wait_for_url(f'**{consulta.RUTA}')
    consulta.consultar_hasta_resultado(cedula_de('jurado_misma_mesa'))
    expect(resultado.aviso_jurado).to_be_visible()


def test_stepper_y_migas_siguen_el_paso_actual(consulta, resultado):
    consulta.abrir()
    expect(consulta.stepper.paso_actual).to_contain_text('Consulta')
    expect(consulta.migas).to_contain_text('Consulta electoral')
    expect(consulta.migas).not_to_contain_text('Resultado')

    consulta.consultar_hasta_resultado(cedula_de('solo_votante'))
    expect(resultado.stepper.paso_actual).to_contain_text('Resultado')
    expect(resultado.migas).to_contain_text('Resultado')


def test_ruta_inexistente_muestra_la_pagina_no_encontrada(consulta, page):
    consulta.abrir(TEXTOS['ruta_inexistente'])
    expect(consulta.titulo).to_have_text('Página no encontrada')
    page.get_by_role('link', name='Volver a la consulta').click()
    page.wait_for_url(f'**{consulta.RUTA}')


# Avisos obligatorios: el sitio no debe parecer oficial

@pytest.mark.parametrize('pantalla', como_parametros('pantallas'))
def test_avisos_de_demostracion_en_todas_las_pantallas(consulta, abrir_pantalla, pantalla):
    abrir_pantalla(pantalla)
    avisos = TEXTOS['avisos_obligatorios']
    expect(consulta.demo_banner.aviso).to_contain_text(avisos['demo'])
    expect(consulta.pie).to_contain_text(avisos['pie'])
    expect(consulta.header.marca).to_contain_text(avisos['marca'])


@pytest.mark.parametrize('escenario', ['solo_votante', 'jurado_misma_mesa'])
def test_resultado_marca_los_datos_como_ficticios(consulta, resultado, escenario):
    consulta.consultar_hasta_resultado(cedula_de(escenario))
    expect(resultado.badge_ficticio).to_be_visible()
    expect(resultado.aclaracion).to_be_visible()


@pytest.mark.parametrize('pantalla', como_parametros('pantallas'))
def test_no_menciona_entidades_reales(consulta, page, abrir_pantalla, pantalla):
    """Regla de marca: ninguna pantalla usa el nombre de la entidad real."""
    abrir_pantalla(pantalla)
    contenido = f'{page.title()} {consulta.texto_visible()}'
    for frase in TEXTOS['frases_prohibidas']:
        assert frase.lower() not in contenido.lower()
