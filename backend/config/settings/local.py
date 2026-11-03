"""Settings para desarrollo local (DEBUG activo, servidor MySQL 8.0 local)."""
from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK, env_bool, env_lista

DEBUG = env_bool('DJANGO_DEBUG', por_defecto=True)
ALLOWED_HOSTS = env_lista('DJANGO_ALLOWED_HOSTS') or ['localhost', '127.0.0.1']

# API navegable de DRF para explorar los endpoints desde el navegador.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
