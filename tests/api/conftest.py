"""Fixtures del nivel API: mensajes de error y contrato de la respuesta (el cliente 'api' está en tests/conftest.py)."""
import pytest

from support.api_client import RUTA_ESQUEMA
from support.data_loader import cargar
from support.openapi import EspecificacionOpenApi


@pytest.fixture(scope='session')
def mensajes_error():
    """Mensaje esperado para cada código de error (textos del Figma)."""
    return cargar('mensajes_error')


@pytest.fixture(scope='session')
def contrato():
    """Claves esperadas y prohibidas de la respuesta de consulta."""
    return cargar('contrato_consulta')


@pytest.fixture(scope='session')
def especificacion(api):
    """Especificación OpenAPI que publica el servidor en ejecución."""
    return EspecificacionOpenApi(api.obtener(RUTA_ESQUEMA, params={'format': 'json'}).json())
