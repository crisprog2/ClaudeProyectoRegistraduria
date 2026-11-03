"""
Manejador central de errores de la API.

Todas las respuestas de error tienen el mismo formato:
    {"codigo": "CEDULA_NO_ENCONTRADA", "mensaje": "No encontramos información para esta cédula."}

El frontend y las pruebas se basan en `codigo` (estable); `mensaje` es el
texto que se muestra al usuario.
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

    codigo, mensaje = next(
        (valor for tipo, valor in ERRORES_DRF.items() if isinstance(exc, tipo)),
        ('ERROR_DE_SOLICITUD', str(getattr(exc, 'detail', 'No se pudo procesar la solicitud.'))),
    )
    respuesta.data = {'codigo': codigo, 'mensaje': mensaje}
    return respuesta
