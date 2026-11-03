"""
Oráculo de edad para las pruebas black-box.

Se implementa aparte del backend a propósito: si el cálculo del servidor
tuviera un defecto, reutilizarlo haría que la prueba lo copiara en vez de detectarlo.
"""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from support import config


def hoy_en_el_servidor():
    """Fecha actual en la zona horaria del servidor."""
    return datetime.now(ZoneInfo(config.ZONA_HORARIA_SERVIDOR)).date()


def edad_esperada(fecha_nacimiento, hoy=None):
    """
    Años cumplidos a la fecha 'hoy' (por defecto, hoy en el servidor).

    fecha_nacimiento es texto ISO ('1990-03-14'). Quien nació un 29 de febrero
    cumple años el 1 de marzo en los años no bisiestos.
    """
    nacimiento = date.fromisoformat(fecha_nacimiento)
    hoy = hoy or hoy_en_el_servidor()
    ya_cumplio = (hoy.month, hoy.day) >= (nacimiento.month, nacimiento.day)
    return hoy.year - nacimiento.year - (0 if ya_cumplio else 1)
