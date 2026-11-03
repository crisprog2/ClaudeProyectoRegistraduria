"""Fixtures del nivel API: cliente HTTP compartido, mensajes de error y contrato de la respuesta."""
import pytest

from support.api_client import ConsultaApiClient
from support.data_loader import cargar


@pytest.fixture(scope='session')
def api():
    """Cliente de la API. Si no hay servidor, detiene la corrida con instrucciones en vez de fallar caso por caso."""
    cliente = ConsultaApiClient()
    if not cliente.servidor_disponible():
        pytest.exit(
            f'No hay un servidor en {cliente.base_url}. Levanta el backend antes de correr tests/api:\n'
            '    $env:CONSULTA_LIMITE_POR_MINUTO = "1000"\n'
            '    cd backend; python manage.py runserver',
            returncode=3,
        )
    yield cliente
    cliente.cerrar()


@pytest.fixture(scope='session')
def mensajes_error():
    """Mensaje esperado para cada código de error (textos del Figma)."""
    return cargar('mensajes_error')


@pytest.fixture(scope='session')
def contrato():
    """Claves esperadas y prohibidas de la respuesta de consulta."""
    return cargar('contrato_consulta')
