"""
Configuración de las pruebas black-box, leída del .env de la raíz del repositorio.

No depende de Django: las pruebas solo conocen las URL de la API y del frontend.
El navegador se elige con las opciones de pytest-playwright (--browser, --headed).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ_REPO = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ_REPO / '.env')

# URL base de la API, sin barra final. Por defecto, el runserver local.
API_BASE_URL = (os.environ.get('API_BASE_URL') or 'http://127.0.0.1:8000').rstrip('/')

# URL base del frontend, sin barra final. Por defecto, el servidor de desarrollo de Vite.
FRONTEND_BASE_URL = (os.environ.get('FRONTEND_BASE_URL') or 'http://localhost:5173').rstrip('/')

# Segundos máximos de espera por respuesta.
TIMEOUT_SEGUNDOS = 10

# Zona horaria del servidor (TIME_ZONE de Django): define el "hoy" con el que se calcula la edad.
ZONA_HORARIA_SERVIDOR = 'America/Bogota'


def contrasena_demo(variable):
    """
    Contraseña de un usuario de demostración, leída de su variable de entorno.

    Son las mismas que usa 'manage.py crear_usuarios_demo' para crear los usuarios. Nunca
    van en los datos de prueba: tests/data/usuarios.json solo dice qué variable usar.
    """
    contrasena = os.environ.get(variable)
    if not contrasena:
        raise RuntimeError(f'Falta {variable} en el .env: es la contraseña de un usuario de demostración.')
    return contrasena
