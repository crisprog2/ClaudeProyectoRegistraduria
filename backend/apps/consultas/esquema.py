"""
Documentación OpenAPI del endpoint de consulta (drf-spectacular).

Vive aparte para que la vista siga delgada. Aquí solo se describe la API: las
reglas siguen en validators.py, services.py y exceptions.py. Los mensajes de
error se toman de esos módulos para que la documentación no repita los textos.
Las pruebas de tests/api/test_documentacion_api.py comparan esta descripción
con las respuestas reales.
"""
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import exceptions, serializers

from .exceptions import ERRORES_DRF
from .serializers import ResultadoConsultaSerializer
from .services import CedulaNoEncontrada
from .validators import CEDULA_FORMATO_INVALIDO, CEDULA_REQUERIDA, MENSAJES

CODIGOS_DE_ERROR = [
    CEDULA_REQUERIDA,
    CEDULA_FORMATO_INVALIDO,
    CedulaNoEncontrada.codigo,
    ERRORES_DRF[exceptions.ParseError][0],
    ERRORES_DRF[exceptions.MethodNotAllowed][0],
    ERRORES_DRF[exceptions.Throttled][0],
]


class SolicitudConsultaSerializer(serializers.Serializer):
    """Cuerpo de la consulta."""
    # Solo documenta: la validación real está en validators.validar_cedula.
    cedula = serializers.RegexField(
        r'^[1-9][0-9]{5,9}$',
        help_text='De 6 a 10 dígitos, sin 0 inicial, puntos, espacios internos ni comas. Los espacios externos se ignoran.',
    )


class ErrorSerializer(serializers.Serializer):
    """Formato común de todas las respuestas de error de la API."""
    codigo = serializers.ChoiceField(choices=CODIGOS_DE_ERROR, help_text='Código estable para usar en los programas.')
    mensaje = serializers.CharField(help_text='Texto para mostrar al usuario.')


def _solicitud(nombre, cedula, descripcion):
    """Ejemplo de cuerpo de la petición, que Swagger UI ofrece en una lista."""
    return OpenApiExample(nombre, value={'cedula': cedula}, description=descripcion, request_only=True)


def _error(http, *errores):
    """Respuesta de error documentada con un ejemplo por cada (nombre, codigo, mensaje)."""
    return OpenApiResponse(
        response=ErrorSerializer,
        examples=[
            OpenApiExample(nombre, value={'codigo': codigo, 'mensaje': mensaje}, response_only=True, status_codes=[http])
            for nombre, codigo, mensaje in errores
        ],
    )


LUGAR_MEDELLIN = {
    'puesto': 'Colegio Cívico La Esperanza',
    'direccion': 'Calle 48 # 65-20',
    'ciudad': 'Medellín',
    'departamento': 'Antioquia',
}

RESPUESTA_EXITOSA = OpenApiResponse(
    response=ResultadoConsultaSerializer,
    description='Persona encontrada. `jurado` es `null` si no tiene designación.',
    examples=[
        OpenApiExample(
            'Solo votante',
            value={
                'ciudadano': {'cedula': '1023456789', 'nombre_completo': 'Laura Camila Gómez', 'edad': 32},
                'lugar_votacion': {'mesa': 12, **LUGAR_MEDELLIN},
                'jurado': None,
            },
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            'Jurado en la misma mesa',
            value={
                'ciudadano': {'cedula': '1098765432', 'nombre_completo': 'Carlos Andrés Martínez', 'edad': 36},
                'lugar_votacion': {'mesa': 18, **LUGAR_MEDELLIN},
                'jurado': {
                    'rol': 'TITULAR',
                    'rol_display': 'Jurado titular',
                    'mesa': 18,
                    **LUGAR_MEDELLIN,
                    'misma_mesa': True,
                },
            },
            response_only=True,
            status_codes=[200],
        ),
    ],
)

_SOLICITUD_INVALIDA = ERRORES_DRF[exceptions.ParseError]

documentar_consulta = extend_schema(
    operation_id='consultar_cedula',
    summary='Consultar lugar de votación y designación como jurado',
    description=(
        'Busca a la persona por su cédula y devuelve su lugar de votación y, si fue designada, '
        'su asignación como jurado.\n\n'
        'La cédula va en el cuerpo y nunca en la URL, para que no quede en logs ni historiales. '
        'No requiere autenticación y tiene un límite de consultas por IP.\n\n'
        '**Todos los datos son ficticios.** Las cédulas de los ejemplos existen solo en los datos de demostración.'
    ),
    tags=['Consulta'],
    request=SolicitudConsultaSerializer,
    examples=[
        _solicitud('Solo votante', '1023456789', 'Responde 200 con `jurado` en `null`.'),
        _solicitud('Jurado', '1098765432', 'Responde 200 con la asignación como jurado.'),
        _solicitud('Cédula no registrada', '1000000000', 'Responde 404.'),
        _solicitud('Formato inválido', '109.876.543', 'Responde 400.'),
    ],
    parameters=[
        OpenApiParameter(
            'Retry-After',
            type=int,
            location=OpenApiParameter.HEADER,
            response=[429],
            description='Segundos que faltan para poder consultar de nuevo.',
        ),
        OpenApiParameter(
            'Allow',
            type=str,
            location=OpenApiParameter.HEADER,
            response=[405],
            description='Métodos permitidos en esta ruta.',
        ),
    ],
    responses={
        200: RESPUESTA_EXITOSA,
        400: _error(
            400,
            ('Cédula requerida', CEDULA_REQUERIDA, MENSAJES[CEDULA_REQUERIDA]),
            ('Formato inválido', CEDULA_FORMATO_INVALIDO, MENSAJES[CEDULA_FORMATO_INVALIDO]),
            ('JSON inválido', *_SOLICITUD_INVALIDA),
        ),
        404: _error(404, ('Cédula no encontrada', CedulaNoEncontrada.codigo, CedulaNoEncontrada.mensaje)),
        405: _error(405, ('Método no permitido', *ERRORES_DRF[exceptions.MethodNotAllowed])),
        415: _error(415, ('El cuerpo no es JSON', *ERRORES_DRF[exceptions.UnsupportedMediaType])),
        429: _error(429, ('Demasiadas consultas', *ERRORES_DRF[exceptions.Throttled])),
    },
)
