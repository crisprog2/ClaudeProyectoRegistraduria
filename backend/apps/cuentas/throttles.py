"""Límite de intentos de inicio de sesión."""
from rest_framework.throttling import AnonRateThrottle


class IngresoRateThrottle(AnonRateThrottle):
    """
    Intentos de inicio de sesión por IP (tasa 'ingreso', 5 por minuto por defecto).

    Frena los ataques de fuerza bruta contra las contraseñas. Cuenta todos los intentos,
    también los exitosos. Igual que el límite de la consulta, identifica al cliente por
    REMOTE_ADDR (NUM_PROXIES = 0), así que no se evade falsificando X-Forwarded-For.
    """
    scope = 'ingreso'
