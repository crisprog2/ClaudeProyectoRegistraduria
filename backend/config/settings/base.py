"""
Settings comunes a todos los entornos.

Toda la configuración sensible o dependiente del entorno se lee de variables
de entorno, cargadas desde el archivo .env de la raíz del repositorio.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Raíz del monorepo, donde vive el .env compartido.
ROOT_DIR = BASE_DIR.parent

load_dotenv(ROOT_DIR / '.env')


def env_requerida(nombre):
    """Devuelve la variable de entorno o falla con un mensaje claro si no existe."""
    valor = os.environ.get(nombre)
    if not valor:
        raise ImproperlyConfigured(f"Falta la variable de entorno obligatoria '{nombre}'. Revisa tu archivo .env.")
    return valor


def env_lista(nombre):
    """Lee una variable separada por comas como lista, ignorando espacios y vacíos."""
    return [item.strip() for item in os.environ.get(nombre, '').split(',') if item.strip()]


def env_bool(nombre, por_defecto=False):
    """Lee una variable como booleano (1, true, yes, si o sí, sin importar mayúsculas); si está vacía usa el valor por defecto."""
    valor = os.environ.get(nombre, '').strip() or str(por_defecto)
    return valor.lower() in ('1', 'true', 'yes', 'si', 'sí')


def env_entero_positivo(nombre, por_defecto):
    """Lee una variable como entero mayor que 0; si está vacía usa el valor por defecto."""
    valor = os.environ.get(nombre, '').strip() or str(por_defecto)
    if not valor.isdigit() or int(valor) == 0:
        raise ImproperlyConfigured(f"La variable '{nombre}' debe ser un entero mayor que 0 (valor actual: '{valor}').")
    return int(valor)


SECRET_KEY = env_requerida('DJANGO_SECRET_KEY')
DEBUG = env_bool('DJANGO_DEBUG')
ALLOWED_HOSTS = env_lista('DJANGO_ALLOWED_HOSTS')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'apps.consultas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CorsMiddleware debe ir antes de CommonMiddleware.
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env_requerida('MYSQL_DATABASE'),
        'USER': env_requerida('MYSQL_USER'),
        'PASSWORD': env_requerida('MYSQL_PASSWORD'),
        'HOST': os.environ.get('MYSQL_HOST', '127.0.0.1'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
        'OPTIONS': {
            # utf8mb4 para tildes, ñ y cualquier carácter Unicode.
            'charset': 'utf8mb4',
            # Modo estricto: MySQL rechaza datos que excedan max_length en vez de truncarlos.
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        # La base de pruebas usa el mismo charset y collation que la base real
        # (utf8mb4_0900_ai_ci, valor por defecto de MySQL 8) para comparar textos igual.
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_0900_ai_ci',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# La API de consulta es pública y de solo lectura: no requiere autenticación.
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Todas las respuestas de error con el formato {codigo, mensaje}.
    'EXCEPTION_HANDLER': 'apps.consultas.exceptions.manejador_de_errores',
    # Límite de consultas por IP para evitar recorridos masivos de cédulas.
    # Por defecto 30/min; la suite black-box levanta el servidor con un valor alto.
    'DEFAULT_THROTTLE_RATES': {'consulta': f"{env_entero_positivo('CONSULTA_LIMITE_POR_MINUTO', 30)}/min"},
    # 0 = identificar al cliente por REMOTE_ADDR. Con el valor por defecto (None)
    # DRF usa X-Forwarded-For, que el cliente puede falsificar para evadir el límite.
    # Si se despliega detrás de un proxy, poner aquí el número de proxies de confianza.
    'NUM_PROXIES': 0,
}

# Documentación OpenAPI en /api/schema/ y Swagger UI en /api/docs/.
SPECTACULAR_SETTINGS = {
    'TITLE': 'ConsultaVoto API',
    'DESCRIPTION': (
        'API de una app **ficticia** de consulta electoral, creada como proyecto de portafolio QA. '
        'Todos los datos son inventados y el sitio no pertenece a ninguna entidad oficial.'
    ),
    'VERSION': '1.0.0',
    # OpenAPI 3.1 usa JSON Schema estándar: las pruebas validan las respuestas sin convertir el esquema.
    'OAS_VERSION': '3.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # Swagger UI se sirve desde el proyecto (drf-spectacular-sidecar), sin CDN.
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
}

CORS_ALLOWED_ORIGINS = env_lista('CORS_ALLOWED_ORIGINS')
