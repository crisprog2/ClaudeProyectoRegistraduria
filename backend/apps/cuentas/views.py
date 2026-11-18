"""
Vistas de la sesión: /api/auth/ingresar/, refrescar/, salir/ y sesion/.

Se mantienen delgadas: las reglas están en services.py, la cookie en cookies.py y la
documentación de Swagger en esquema.py. Los errores los traduce el manejador central
(apps/consultas/exceptions.py) al formato {"codigo", "mensaje"}.
"""
from django.conf import settings
from rest_framework import exceptions, status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import esquema
from .cookies import borrar_cookie_refresco, leer_cookie_refresco, poner_cookie_refresco
from .excepciones import DEMASIADOS_INTENTOS, USA_GET, USA_POST, DatosIncompletos, SolicitudRechazada
from .permissions import TieneRolEnLaApp
from .roles import rol_de
from .serializers import RespuestaIngresoSerializer, UsuarioSesionSerializer, datos_sesion, datos_usuario
from .services import cerrar_sesion, iniciar_sesion, renovar_sesion
from .throttles import IngresoRateThrottle

SOLO_POST = {exceptions.MethodNotAllowed: USA_POST}


def exigir_cabecera_de_la_app(request):
    """
    Rechaza la petición si no trae la cabecera propia (settings.CABECERA_APP).

    Un sitio ajeno no puede agregar cabeceras propias sin una verificación de CORS, que
    solo permite el origen del frontend. Junto con SameSite=Strict protege contra CSRF.
    """
    nombre, valor = settings.CABECERA_APP
    if request.headers.get(nombre) != valor:
        raise SolicitudRechazada()


def respuesta_con_sesion(sesion):
    """200 con el token de acceso en el JSON y el de refresco en la cookie."""
    respuesta = Response(RespuestaIngresoSerializer(datos_sesion(sesion)).data)
    poner_cookie_refresco(respuesta, sesion.refresco, sesion.segundos_refresco)
    return respuesta


class IngresarView(APIView):
    """POST /api/auth/ingresar/ con {"usuario", "contrasena"}."""
    # Sin autenticación: un token inválido en la cabecera no debe impedir iniciar sesión.
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [IngresoRateThrottle]
    errores_drf = {**SOLO_POST, exceptions.Throttled: DEMASIADOS_INTENTOS}

    @esquema.documentar_ingresar
    def post(self, request):
        """Inicia sesión: valida los datos, las credenciales y el rol, y entrega los tokens."""
        if not isinstance(request.data, dict):
            raise ParseError()
        usuario, contrasena = request.data.get('usuario'), request.data.get('contrasena')
        if not all(isinstance(valor, str) and valor.strip() for valor in (usuario, contrasena)):
            raise DatosIncompletos()
        return respuesta_con_sesion(iniciar_sesion(request, usuario.strip(), contrasena))


class RefrescarView(APIView):
    """POST /api/auth/refrescar/ (sin cuerpo): renueva el token de acceso con la cookie."""
    authentication_classes = []
    permission_classes = [AllowAny]
    errores_drf = SOLO_POST

    @esquema.documentar_refrescar
    def post(self, request):
        """Rota el token de refresco de la cookie y entrega un token de acceso nuevo."""
        exigir_cabecera_de_la_app(request)
        return respuesta_con_sesion(renovar_sesion(leer_cookie_refresco(request)))


class SalirView(APIView):
    """POST /api/auth/salir/: revoca el token de refresco y borra la cookie."""
    authentication_classes = []
    permission_classes = [AllowAny]
    errores_drf = SOLO_POST

    @esquema.documentar_salir
    def post(self, request):
        """Cierra la sesión. Responde 204 aunque la sesión ya no existiera."""
        exigir_cabecera_de_la_app(request)
        cerrar_sesion(leer_cookie_refresco(request))
        respuesta = Response(status=status.HTTP_204_NO_CONTENT)
        borrar_cookie_refresco(respuesta)
        return respuesta


class SesionView(APIView):
    """GET /api/auth/sesion/ con el token de acceso: quién soy y qué rol tengo."""
    permission_classes = [IsAuthenticated, TieneRolEnLaApp]
    errores_drf = {exceptions.MethodNotAllowed: USA_GET}

    @esquema.documentar_sesion
    def get(self, request):
        """Datos del usuario del token, con su rol leído de la base de datos."""
        return Response(UsuarioSesionSerializer(datos_usuario(request.user, rol_de(request.user))).data)
