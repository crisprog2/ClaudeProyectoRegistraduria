"""
Manejador central de errores de la API.

Todas las respuestas de error tienen el mismo formato:
    {"codigo": "CEDULA_NO_ENCONTRADA", "mensaje": "No encontramos información para esta cédula."}

El frontend y las pruebas se basan en `codigo` (estable); `mensaje` es el
texto que se muestra al usuario.

Cómo se elige el código de un error de DRF, en este orden:
1. Si la excepción trae su propio `codigo` (errores de apps/cuentas/excepciones.py).
2. Si la vista define `errores_drf`, sus textos para ese tipo de error. Así cada ruta
   puede tener su mensaje, p. ej. el 405 de la consulta dice "Usa POST para consultar."
3. ERRORES_DRF, los textos comunes de la API.
4. ERROR_DE_SOLICITUD con el texto de DRF, para cualquier otro error.
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .services import CedulaNoEncontrada
from .validators import MENSAJES as MENSAJES_CEDULA

# Errores propios de DRF -> (codigo, mensaje). Se conserva el código HTTP y
# las cabeceras que agrega DRF (p. ej. Retry-After en el 429).
ERRORES_DRF = {
    exceptions.Throttled: ('DEMASIADAS_CONSULTAS', 'Hiciste demasiadas consultas. Intenta de nuevo en unos segundos.'),
    exceptions.MethodNotAllowed: ('METODO_NO_PERMITIDO', 'Usa POST para consultar.'),
    exceptions.ParseError: ('SOLICITUD_INVALIDA', 'La solicitud no tiene un formato válido.'),
    exceptions.UnsupportedMediaType: ('SOLICITUD_INVALIDA', 'La solicitud no tiene un formato válido.'),
    # Autenticación con JWT (apps/cuentas). InvalidToken de simplejwt hereda de AuthenticationFailed.
    exceptions.NotAuthenticated: ('NO_AUTENTICADO', 'Inicia sesión para continuar.'),
    exceptions.AuthenticationFailed: ('TOKEN_INVALIDO', 'Tu sesión no es válida o venció. Inicia sesión de nuevo.'),
    exceptions.PermissionDenied: ('SIN_PERMISO', 'No tienes permiso para realizar esta acción.'),
}


def _error(codigo, mensaje, http_status):
    """Respuesta de error con el cuerpo estándar {codigo, mensaje}."""
    return Response({'codigo': codigo, 'mensaje': mensaje}, status=http_status)


def manejador_de_errores(exc, context):
    """EXCEPTION_HANDLER de DRF: traduce cualquier error de la API al formato {codigo, mensaje}."""
    if isinstance(exc, DjangoValidationError) and exc.code in MENSAJES_CEDULA:
        return _error(exc.code, exc.messages[0], status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, CedulaNoEncontrada):
        return _error(exc.codigo, exc.mensaje, status.HTTP_404_NOT_FOUND)

    respuesta = exception_handler(exc, context)
    if respuesta is None:
        return None  # Error no controlado: Django responde 500.

    respuesta.data = dict(zip(('codigo', 'mensaje'), _codigo_y_mensaje(exc, context)))
    return respuesta


def _codigo_y_mensaje(exc, context):
    """(codigo, mensaje) de un error de DRF, según el orden descrito en el docstring del módulo."""
    if getattr(exc, 'codigo', None):
        return exc.codigo, str(exc.detail)
    propios = getattr(context.get('view'), 'errores_drf', {})
    for tipo, valor in (*propios.items(), *ERRORES_DRF.items()):
        if isinstance(exc, tipo):
            return valor
    return 'ERROR_DE_SOLICITUD', str(getattr(exc, 'detail', 'No se pudo procesar la solicitud.'))
