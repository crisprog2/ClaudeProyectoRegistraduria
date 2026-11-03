"""
Pruebas black-box de las consultas exitosas: solo votantes y jurados.

Los escenarios y la respuesta esperada vienen de tests/data/ciudadanos.json;
la edad se calcula con el oráculo de support/edad.py.
"""
import pytest

from support.data_loader import caso, como_parametros
from support.edad import edad_esperada

pytestmark = pytest.mark.api


def claves_anidadas(valor):
    """Todas las claves de un JSON, a cualquier profundidad."""
    if isinstance(valor, dict):
        for clave, hijo in valor.items():
            yield clave
            yield from claves_anidadas(hijo)
    elif isinstance(valor, list):
        for hijo in valor:
            yield from claves_anidadas(hijo)


@pytest.mark.parametrize('ciudadano', como_parametros('ciudadanos'))
def test_respuesta_completa_por_escenario(api, ciudadano):
    respuesta = api.consultar(ciudadano['cedula'])

    assert respuesta.status_code == 200
    assert respuesta.headers['Content-Type'].startswith('application/json')
    esperado = ciudadano['esperado']
    assert respuesta.json() == {
        'ciudadano': {**esperado['ciudadano'], 'edad': edad_esperada(ciudadano['fecha_nacimiento'])},
        'lugar_votacion': esperado['lugar_votacion'],
        'jurado': esperado['jurado'],
    }


@pytest.mark.smoke
def test_solo_votante_no_tiene_designacion(api):
    cuerpo = api.consultar(caso('ciudadanos', 'solo_votante')['cedula']).json()

    assert cuerpo['lugar_votacion'] is not None
    assert cuerpo['jurado'] is None


@pytest.mark.smoke
def test_jurado_en_la_misma_mesa_sirve_donde_vota(api):
    cuerpo = api.consultar(caso('ciudadanos', 'jurado_misma_mesa')['cedula']).json()
    jurado, lugar = cuerpo['jurado'], cuerpo['lugar_votacion']

    assert jurado['misma_mesa'] is True
    assert {clave: jurado[clave] for clave in lugar} == lugar


@pytest.mark.smoke
def test_jurado_en_otra_mesa_del_mismo_puesto(api):
    cuerpo = api.consultar(caso('ciudadanos', 'jurado_otra_mesa_mismo_puesto')['cedula']).json()
    jurado, lugar = cuerpo['jurado'], cuerpo['lugar_votacion']

    assert jurado['misma_mesa'] is False
    assert jurado['puesto'] == lugar['puesto']
    assert jurado['mesa'] != lugar['mesa']


@pytest.mark.smoke
def test_jurado_en_otro_puesto(api):
    cuerpo = api.consultar(caso('ciudadanos', 'jurado_otro_puesto')['cedula']).json()
    jurado, lugar = cuerpo['jurado'], cuerpo['lugar_votacion']

    assert jurado['misma_mesa'] is False
    assert jurado['puesto'] != lugar['puesto']
    assert jurado['direccion'] != lugar['direccion']


def test_espacios_externos_se_ignoran(api):
    cedula = caso('ciudadanos', 'solo_votante_cedula_7_digitos')['cedula']

    respuesta = api.consultar(f'  {cedula}  ')

    assert respuesta.status_code == 200
    assert respuesta.json()['ciudadano']['cedula'] == cedula


@pytest.mark.parametrize('id_escenario', ['solo_votante', 'jurado_misma_mesa'])
def test_contrato_de_claves(api, contrato, id_escenario):
    cuerpo = api.consultar(caso('ciudadanos', id_escenario)['cedula']).json()

    assert list(cuerpo) == contrato['claves_raiz']
    assert list(cuerpo['ciudadano']) == contrato['claves_ciudadano']
    assert list(cuerpo['lugar_votacion']) == contrato['claves_lugar_votacion']
    if cuerpo['jurado'] is not None:
        assert list(cuerpo['jurado']) == contrato['claves_jurado']


@pytest.mark.parametrize('ciudadano', como_parametros('ciudadanos'))
def test_no_expone_datos_sensibles(api, contrato, ciudadano):
    """Ni el género, ni la fecha de nacimiento, ni IDs internos aparecen en la respuesta."""
    respuesta = api.consultar(ciudadano['cedula'])

    assert not set(claves_anidadas(respuesta.json())) & set(contrato['claves_prohibidas'])
    assert ciudadano['fecha_nacimiento'] not in respuesta.text
