"""
Fixtures de los steps contra la interfaz.

Entre steps, el estado viaja en la fixture 'ciudadano' (caso de tests/data/ciudadanos.json)
y en la propia página del navegador, a través de los Page Objects 'consulta' y 'resultado'.

La fixture automática '_un_escenario_por_navegador' hace que cada escenario se repita
por navegador, como las pruebas E2E. Ver su docstring.
"""
import pytest

from step_defs.interfaz.common_steps import *  # noqa: F401,F403


@pytest.fixture(autouse=True)
def _un_escenario_por_navegador(page):
    """
    Pide la página del navegador desde la definición de cada escenario.

    pytest-playwright repite una prueba por cada --browser solo si 'page' (o
    'browser_name') forma parte de las fixtures que la prueba declara. Los escenarios
    de pytest-bdd no la declaran: cada step la obtiene al ejecutarse, a través de los
    Page Objects. Sin esta fixture, con varios navegadores cada escenario se recogía una
    sola vez y corría solo en el primero (pytest-playwright lo avisa con el warning
    "specifying multiple browsers is not supported"). Además, como el resultado no
    llevaba el navegador como parámetro, Allure juntaba los resultados de los trabajos
    de Chromium, Firefox y WebKit del CI como si fueran repeticiones de una misma prueba.

    Al ser automática y depender de 'page', el escenario se recoge una vez por
    navegador ([chromium], [firefox], [webkit]) y el reporte los muestra por separado.
    La página es la misma que reciben los Page Objects: no se abre otra.
    """
    return page


@pytest.fixture(scope='session', autouse=True)
def exigir_aplicacion(aplicacion_levantada):
    """Detiene la corrida con instrucciones si falta el backend o el frontend."""
