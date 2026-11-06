"""Pruebas white-box de la documentación OpenAPI: validez, rutas y el caso 429."""
import pytest
from django.core.management import call_command
from django.urls import reverse


@pytest.fixture
def especificacion(cliente):
    """Especificación OpenAPI en JSON."""
    return cliente.get(reverse('esquema-api'), {'format': 'json'}).json()


def test_especificacion_valida_y_sin_advertencias(tmp_path):
    """Falla si drf-spectacular no puede deducir un tipo o si el esquema no cumple OpenAPI."""
    call_command('spectacular', validate=True, fail_on_warn=True, file=str(tmp_path / 'esquema.yml'))


def test_especificacion_usa_openapi_31(especificacion):
    assert especificacion['openapi'] == '3.1.0'


def test_swagger_ui_no_depende_de_un_cdn(cliente):
    respuesta = cliente.get(reverse('documentacion-api'))

    assert respuesta.status_code == 200
    html = respuesta.content.decode()
    assert 'swagger-ui-bundle' in html
    assert 'cdn.' not in html


def test_jurado_documenta_la_ubicacion_de_la_mesa_de_servicio(especificacion):
    jurado = especificacion['components']['schemas']['Jurado']

    assert {'mesa', 'puesto', 'direccion', 'ciudad', 'departamento'} <= set(jurado['required'])
    assert jurado['properties']['misma_mesa']['type'] == 'boolean'


def test_respuesta_429_real_coincide_con_la_documentada(consultar, especificacion):
    """El límite solo se puede agotar aquí: la suite black-box corre con un límite alto."""
    for _ in range(30):
        consultar('1098765432')
    real = consultar('1098765432')

    documentada = especificacion['paths']['/api/consulta/']['post']['responses']['429']
    ejemplos = documentada['content']['application/json']['examples'].values()
    assert real.status_code == 429
    assert real.json() in [ejemplo['value'] for ejemplo in ejemplos]
    assert 'Retry-After' in real.headers
    assert 'Retry-After' in documentada['headers']
