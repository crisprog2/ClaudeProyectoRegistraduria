"""
Settings para la ejecución de pruebas con pytest-django.

Usa el mismo motor que producción (MySQL) para que las restricciones, los
largos máximos y el modo estricto se comporten igual que en la realidad.
pytest-django crea y destruye la base 'test_<MYSQL_DATABASE>' en cada corrida.
"""
from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Límites fijos: las pruebas del 429 no deben depender de CONSULTA_LIMITE_POR_MINUTO ni de
# INGRESO_LIMITE_POR_MINUTO del .env.
REST_FRAMEWORK = {**REST_FRAMEWORK, 'DEFAULT_THROTTLE_RATES': {'consulta': '30/min', 'ingreso': '5/min'}}  # noqa: F405

# Cookie sin Secure, como en local: las pruebas que lo activan lo hacen con override_settings.
JWT_COOKIE = {**JWT_COOKIE, 'SECURE': False}  # noqa: F405

# Hash de contraseñas rápido: solo afecta la velocidad de las pruebas.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
