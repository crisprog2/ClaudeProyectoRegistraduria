"""Pruebas E2E de Swagger UI: carga en el navegador sin servicios externos y permite probar la API."""
from urllib.parse import urlparse

import pytest
from playwright.sync_api import expect

from support import config
from support.data_loader import caso
from support.pages.documentacion_api_page import DocumentacionApiPage

pytestmark = pytest.mark.e2e


@pytest.fixture
def documentacion(page):
    """Page Object de Swagger UI."""
    return DocumentacionApiPage(page, config.API_BASE_URL)


def test_muestra_la_api_sin_pedir_nada_a_servicios_externos(page, documentacion):
    urls = []
    page.on('request', lambda peticion: urls.append(urlparse(peticion.url)))

    documentacion.abrir()

    expect(documentacion.operacion).to_be_visible()
    # Los recursos incrustados (data:, blob:) no salen a la red.
    assert {url.netloc for url in urls if url.scheme in ('http', 'https')} == {urlparse(config.API_BASE_URL).netloc}


def test_probar_la_api_desde_swagger_responde_el_ejemplo(documentacion):
    documentacion.abrir()

    http, cuerpo = documentacion.ejecutar_ejemplo_por_defecto()

    assert http == 200
    assert cuerpo['ciudadano']['cedula'] == caso('ciudadanos', 'solo_votante')['cedula']
    assert cuerpo['jurado'] is None
