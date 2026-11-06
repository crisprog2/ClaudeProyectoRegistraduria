"""
Fixtures de los steps contra la interfaz.

Entre steps, el estado viaja en la fixture 'ciudadano' (caso de tests/data/ciudadanos.json)
y en la propia página del navegador, a través de los Page Objects 'consulta' y 'resultado'.
"""
import pytest

from step_defs.interfaz.common_steps import *  # noqa: F401,F403


@pytest.fixture(scope='session', autouse=True)
def exigir_aplicacion(aplicacion_levantada):
    """Detiene la corrida con instrucciones si falta el backend o el frontend."""
