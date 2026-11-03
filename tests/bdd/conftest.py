"""
Fixtures del nivel BDD.

Los steps comunes se importan aquí para que estén disponibles en todos los
features. Entre steps, el estado viaja en fixtures creadas con target_fixture:
'ciudadano' (caso de tests/data/ciudadanos.json) y 'respuesta' (respuesta HTTP).
Por ahora los steps ejecutan contra la API; cuando exista el frontend, los
mismos features podrán ejecutarse contra la interfaz con otros steps.
"""
from step_defs.common_steps import *  # noqa: F401,F403
