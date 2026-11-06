"""
Fixtures de nivel raíz de las pruebas black-box (API, BDD y E2E).

La configuración (.env) se lee en support/config.py y los datos de prueba en
support/data_loader.py; cada nivel agrega sus fixtures en su propio conftest.py.
"""
import pytest
import requests

from support import config
from support.api_client import ConsultaApiClient
from support.pages.consulta_page import ConsultaPage
from support.pages.resultado_page import ResultadoPage

COMO_LEVANTAR_BACKEND = (
    '    $env:CONSULTA_LIMITE_POR_MINUTO = "1000"\n'
    '    cd backend; python manage.py runserver'
)


@pytest.fixture(scope='session')
def api():
    """Cliente de la API compartido por las suites API y BDD.

    Si no hay servidor, detiene la corrida con instrucciones en vez de fallar caso por caso.
    """
    cliente = ConsultaApiClient()
    if not cliente.servidor_disponible():
        pytest.exit(
            f'No hay un servidor en {cliente.base_url}. Levanta el backend antes de correr las pruebas:\n'
            f'{COMO_LEVANTAR_BACKEND}',
            returncode=3,
        )
    yield cliente
    cliente.cerrar()


@pytest.fixture(scope='session')
def base_url():
    """URL del frontend: pytest-playwright la usa para resolver las rutas relativas de page.goto()."""
    return config.FRONTEND_BASE_URL


@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    """Ventana del tamaño del Figma (1440 px) e idioma de la aplicación para todas las pruebas de interfaz."""
    return {**browser_context_args, 'viewport': {'width': 1440, 'height': 900}, 'locale': 'es-CO'}


@pytest.fixture(scope='session')
def aplicacion_levantada(api):
    """Exige el backend (fixture api) y el frontend; las pruebas de interfaz dependen de los dos."""
    try:
        requests.get(config.FRONTEND_BASE_URL, timeout=config.TIMEOUT_SEGUNDOS)
    except requests.ConnectionError:
        pytest.exit(
            f'No hay un frontend en {config.FRONTEND_BASE_URL}. Levántalo antes de correr las pruebas de interfaz:\n'
            '    cd frontend; npm run dev',
            returncode=3,
        )


@pytest.fixture
def consulta(page):
    """Page Object de la pantalla de consulta (compartido por BDD y E2E)."""
    return ConsultaPage(page)


@pytest.fixture
def resultado(page):
    """Page Object de la pantalla de resultado (compartido por BDD y E2E)."""
    return ResultadoPage(page)
