"""
Documentación OpenAPI de la sesión (drf-spectacular).

Igual que apps/consultas/esquema.py: aquí solo se describe la API, y los mensajes se
toman de excepciones.py, de las vistas y del manejador central para no repetir textos.
Las pruebas de tests/api/test_documentacion_api.py comparan esta descripción con las
respuestas reales.
"""
from django.conf import settings
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import exceptions, serializers

from apps.consultas.exceptions import ERRORES_DRF

from .excepciones import (
    DEMASIADOS_INTENTOS, USA_GET, USA_POST, CredencialesInvalidas, DatosIncompletos, SesionExpirada,
    SolicitudRechazada,
)
from .serializers import RespuestaIngresoSerializer, SolicitudIngresoSerializer, UsuarioSesionSerializer

ETIQUETA = ['Sesión']
NOMBRE_COOKIE = settings.JWT_COOKIE['NOMBRE']
NOMBRE_CABECERA, VALOR_CABECERA = settings.CABECERA_APP


def _de(excepcion):
    """(codigo, mensaje) de una excepción propia de excepciones.py."""
    return excepcion.codigo, str(excepcion.default_detail)


CODIGOS_DE_ERROR = sorted({
    *(codigo for codigo, _ in map(_de, (DatosIncompletos, CredencialesInvalidas, SesionExpirada, SolicitudRechazada))),
    DEMASIADOS_INTENTOS[0], USA_POST[0],
    ERRORES_DRF[exceptions.ParseError][0],
    ERRORES_DRF[exceptions.NotAuthenticated][0],
    ERRORES_DRF[exceptions.AuthenticationFailed][0],
    ERRORES_DRF[exceptions.PermissionDenied][0],
})


class ErrorSesionSerializer(serializers.Serializer):
    """Formato común de las respuestas de error de la sesión."""
    codigo = serializers.ChoiceField(choices=CODIGOS_DE_ERROR, help_text='Código estable para usar en los programas.')
    mensaje = serializers.CharField(help_text='Texto para mostrar al usuario.')


def _error(http, *errores):
    """Respuesta de error con un ejemplo por cada (nombre, (codigo, mensaje))."""
    return OpenApiResponse(
        response=ErrorSesionSerializer,
        examples=[
            OpenApiExample(nombre, value={'codigo': codigo, 'mensaje': mensaje}, response_only=True, status_codes=[http])
            for nombre, (codigo, mensaje) in errores
        ],
    )


USUARIO_EJEMPLO = {'usuario': 'analista.demo', 'nombre': 'Analista Demo', 'rol': 'Analista'}
# Token de muestra, abreviado: no es un token válido.
ACCESO_EJEMPLO = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIn0.firma'

RESPUESTA_CON_SESION = OpenApiResponse(
    response=RespuestaIngresoSerializer,
    description=(
        f'Sesión iniciada. El token de refresco llega **solo** en la cookie `{NOMBRE_COOKIE}` '
        '(HttpOnly, SameSite=Strict, Path=/api/auth/), nunca en el cuerpo.'
    ),
    examples=[OpenApiExample(
        'Sesión de analista',
        value={'acceso': ACCESO_EJEMPLO, 'tipo': 'Bearer', 'expira_en': 900, 'usuario': USUARIO_EJEMPLO},
        response_only=True, status_codes=[200],
    )],
)

SET_COOKIE = OpenApiParameter(
    'Set-Cookie', type=str, location=OpenApiParameter.HEADER, response=[200],
    description=f'Cookie `{NOMBRE_COOKIE}` con el token de refresco (HttpOnly, SameSite=Strict, Path=/api/auth/).',
)
CABECERA_APP = OpenApiParameter(
    NOMBRE_CABECERA, type=str, location=OpenApiParameter.HEADER, required=True, enum=[VALOR_CABECERA],
    description=f'Debe valer `{VALOR_CABECERA}`. Protege contra peticiones falsificadas desde otro sitio (CSRF).',
)
COOKIE_REFRESCO = OpenApiParameter(
    NOMBRE_COOKIE, type=str, location=OpenApiParameter.COOKIE, required=False,
    description='Token de refresco. La envía el navegador automáticamente; JavaScript no puede leerla.',
)
SIN_CABECERA = _error(403, ('Sin la cabecera de la aplicación', _de(SolicitudRechazada)))

documentar_ingresar = extend_schema(
    operation_id='iniciar_sesion',
    summary='Iniciar sesión',
    description=(
        'Para el **Administrador** y el **Analista**. Devuelve el token de acceso (15 minutos) y deja el '
        'token de refresco en una cookie HttpOnly (la sesión dura como máximo 8 horas).\n\n'
        'Un usuario inexistente, una contraseña incorrecta, un usuario desactivado o sin rol reciben el '
        'mismo error, para no revelar qué cuentas existen. Hay un límite de intentos por IP.\n\n'
        '**Todos los datos son ficticios.**'
    ),
    tags=ETIQUETA,
    request=SolicitudIngresoSerializer,
    examples=[OpenApiExample('Analista de demostración', value={'usuario': 'analista.demo', 'contrasena': '********'}, request_only=True)],
    parameters=[
        SET_COOKIE,
        OpenApiParameter('Retry-After', type=int, location=OpenApiParameter.HEADER, response=[429],
                         description='Segundos que faltan para poder intentarlo de nuevo.'),
        OpenApiParameter('Allow', type=str, location=OpenApiParameter.HEADER, response=[405],
                         description='Métodos permitidos en esta ruta.'),
    ],
    responses={
        200: RESPUESTA_CON_SESION,
        400: _error(400, ('Datos incompletos', _de(DatosIncompletos)),
                    ('JSON inválido', ERRORES_DRF[exceptions.ParseError])),
        401: _error(401, ('Credenciales inválidas', _de(CredencialesInvalidas))),
        405: _error(405, ('Método no permitido', USA_POST)),
        415: _error(415, ('El cuerpo no es JSON', ERRORES_DRF[exceptions.UnsupportedMediaType])),
        429: _error(429, ('Demasiados intentos', DEMASIADOS_INTENTOS)),
    },
)

documentar_refrescar = extend_schema(
    operation_id='renovar_sesion',
    summary='Renovar el token de acceso',
    description=(
        'Usa la cookie del token de refresco: la revoca y entrega una nueva (rotación) con un token de '
        'acceso nuevo. La nueva conserva el vencimiento de la original, así que la sesión no se alarga '
        'más de 8 horas. No lleva cuerpo.'
    ),
    tags=ETIQUETA,
    request=None,
    parameters=[CABECERA_APP, COOKIE_REFRESCO, SET_COOKIE],
    responses={
        200: RESPUESTA_CON_SESION,
        401: _error(401, ('Sesión vencida o revocada', _de(SesionExpirada))),
        403: SIN_CABECERA,
        405: _error(405, ('Método no permitido', USA_POST)),
    },
)

documentar_salir = extend_schema(
    operation_id='cerrar_sesion',
    summary='Cerrar sesión',
    description=(
        'Revoca el token de refresco de la cookie y la borra. Responde 204 aunque la sesión ya no existiera. '
        'El token de acceso ya entregado vence solo (15 minutos como máximo): el frontend lo descarta de su memoria.'
    ),
    tags=ETIQUETA,
    request=None,
    parameters=[CABECERA_APP, COOKIE_REFRESCO],
    responses={
        204: OpenApiResponse(description='Sesión cerrada y cookie borrada.'),
        403: SIN_CABECERA,
        405: _error(405, ('Método no permitido', USA_POST)),
    },
)

documentar_sesion = extend_schema(
    operation_id='consultar_sesion',
    summary='Usuario de la sesión',
    description=(
        'Devuelve el usuario del token de acceso y su rol. El rol se lee de la base de datos en cada petición: '
        'si el usuario fue desactivado o perdió el rol, el acceso se pierde de inmediato.'
    ),
    tags=ETIQUETA,
    parameters=[
        OpenApiParameter('WWW-Authenticate', type=str, location=OpenApiParameter.HEADER, response=[401],
                         description='Esquema de autenticación esperado: `Bearer realm="api"`.'),
    ],
    responses={
        200: OpenApiResponse(response=UsuarioSesionSerializer, examples=[
            OpenApiExample('Analista', value=USUARIO_EJEMPLO, response_only=True, status_codes=[200]),
        ]),
        401: _error(401, ('Sin token', ERRORES_DRF[exceptions.NotAuthenticated]),
                    ('Token inválido o vencido', ERRORES_DRF[exceptions.AuthenticationFailed])),
        403: _error(403, ('Usuario sin rol', ERRORES_DRF[exceptions.PermissionDenied])),
        405: _error(405, ('Método no permitido', USA_GET)),
    },
)
