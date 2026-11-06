"""
Fixtures del nivel E2E: datos de la interfaz y apertura de cada pantalla.

El navegador, el contexto y la página los aporta pytest-playwright; la URL del frontend
y los Page Objects 'consulta' y 'resultado' están en tests/conftest.py.
"""
import pytest

from support.data_loader import caso, cargar


@pytest.fixture(scope='session', autouse=True)
def exigir_aplicacion(aplicacion_levantada):
    """Detiene la corrida con instrucciones si falta el backend o el frontend."""


@pytest.fixture(scope='session')
def textos():
    """Textos esperados en pantalla (tests/data/textos_interfaz.json)."""
    return cargar('textos_interfaz')


@pytest.fixture(scope='session')
def mensajes_error():
    """Mensaje esperado para cada código de error (textos del Figma)."""
    return cargar('mensajes_error')


@pytest.fixture
def abrir_pantalla(consulta):
    """Función que deja la página en una pantalla de tests/data/pantallas.json."""
    def _abrir(pantalla):
        """Consulta, provoca el error o abre la ruta que indique la pantalla, y espera a que aparezca."""
        if 'ruta' in pantalla:
            consulta.abrir(pantalla['ruta'])
        elif 'escenario' in pantalla:
            consulta.consultar_hasta_resultado(caso('ciudadanos', pantalla['escenario'])['cedula'])
        else:
            consulta.abrir()
            if 'valor' in pantalla:
                consulta.consultar(pantalla['valor'])
                consulta.alerta.wait_for()
    return _abrir


@pytest.fixture
def peticiones_api(page):
    """Lista que se llena con cada petición que la página hace a la API."""
    peticiones = []
    page.on('request', lambda peticion: peticiones.append(peticion) if '/api/' in peticion.url else None)
    return peticiones
