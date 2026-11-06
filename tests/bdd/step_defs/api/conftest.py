"""
Fixtures de los steps contra la API.

Entre steps, el estado viaja en fixtures creadas con target_fixture:
'ciudadano' (caso de tests/data/ciudadanos.json) y 'respuesta' (respuesta HTTP).
"""
from step_defs.api.common_steps import *  # noqa: F401,F403
