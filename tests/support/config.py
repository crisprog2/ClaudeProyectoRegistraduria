"""
Configuración de las pruebas black-box, leída del .env de la raíz del repositorio.

No depende de Django: las pruebas solo conocen la URL de la API.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ_REPO = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ_REPO / '.env')

# URL base de la API, sin barra final. Por defecto, el runserver local.
API_BASE_URL = (os.environ.get('API_BASE_URL') or 'http://127.0.0.1:8000').rstrip('/')

# Segundos máximos de espera por respuesta.
TIMEOUT_SEGUNDOS = 10

# Zona horaria del servidor (TIME_ZONE de Django): define el "hoy" con el que se calcula la edad.
ZONA_HORARIA_SERVIDOR = 'America/Bogota'
