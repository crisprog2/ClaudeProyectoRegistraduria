"""
Fixtures de nivel raíz de las pruebas black-box (API, BDD y E2E).

La configuración (.env) se lee en support/config.py y los datos de prueba en
support/data_loader.py; cada nivel agrega sus fixtures en su propio conftest.py.
"""
import pytest

from support.api_client import ConsultaApiClient


@pytest.fixture(scope='session')
def api():
    """Cliente de la API compartido por las suites API y BDD.

    Si no hay servidor, detiene la corrida con instrucciones en vez de fallar caso por caso.
    """
    cliente = ConsultaApiClient()
    if not cliente.servidor_disponible():
        pytest.exit(
            f'No hay un servidor en {cliente.base_url}. Levanta el backend antes de correr las pruebas:\n'
            '    $env:CONSULTA_LIMITE_POR_MINUTO = "1000"\n'
            '    cd backend; python manage.py runserver',
            returncode=3,
        )
    yield cliente
    cliente.cerrar()
