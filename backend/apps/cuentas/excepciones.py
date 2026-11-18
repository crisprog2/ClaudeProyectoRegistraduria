"""
Errores propios del inicio de sesión.

Cada uno lleva su `codigo` estable. El manejador central (apps/consultas/exceptions.py)
lo usa para responder con el formato común {"codigo", "mensaje"}.
"""
from rest_framework import status
from rest_framework.exceptions import APIException

# Cabecera WWW-Authenticate de las respuestas 401, como exige HTTP. Es la misma que usa simplejwt.
DESAFIO_BEARER = 'Bearer realm="api"'

# (codigo, mensaje) de errores de DRF con texto propio en las rutas de la sesión. Las vistas
# los usan en errores_drf y esquema.py en la documentación, para no repetir los textos.
DEMASIADOS_INTENTOS = ('DEMASIADOS_INTENTOS', 'Hiciste demasiados intentos. Espera un minuto e inténtalo de nuevo.')
USA_POST = ('METODO_NO_PERMITIDO', 'Usa POST en esta ruta.')
USA_GET = ('METODO_NO_PERMITIDO', 'Usa GET en esta ruta.')


class ErrorConCodigo(APIException):
    """Error de la API con un código propio; `default_detail` es el mensaje para el usuario."""
    codigo = 'ERROR_DE_SOLICITUD'


class DatosIncompletos(ErrorConCodigo):
    """Falta el usuario o la contraseña."""
    status_code = status.HTTP_400_BAD_REQUEST
    codigo = 'DATOS_INCOMPLETOS'
    default_detail = 'Escribe tu usuario y tu contraseña.'


class CredencialesInvalidas(ErrorConCodigo):
    """
    El usuario no puede iniciar sesión en la aplicación.

    Es el mismo error para un usuario inexistente, una contraseña incorrecta, un usuario
    desactivado, un usuario sin rol y el superusuario. Así nadie puede averiguar qué
    usuarios existen ni si acertó la contraseña de una cuenta sin acceso.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    codigo = 'CREDENCIALES_INVALIDAS'
    default_detail = 'Usuario o contraseña incorrectos.'
    auth_header = DESAFIO_BEARER


class SesionExpirada(ErrorConCodigo):
    """La cookie del token de refresco falta, venció, fue revocada o su usuario ya no tiene acceso."""
    status_code = status.HTTP_401_UNAUTHORIZED
    codigo = 'SESION_EXPIRADA'
    default_detail = 'Tu sesión terminó. Inicia sesión de nuevo.'
    auth_header = DESAFIO_BEARER


class SolicitudRechazada(ErrorConCodigo):
    """La petición no trae la cabecera propia de la aplicación (protección contra CSRF)."""
    status_code = status.HTTP_403_FORBIDDEN
    codigo = 'SOLICITUD_RECHAZADA'
    default_detail = 'La solicitud no proviene de la aplicación.'
