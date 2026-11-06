"""Vista DRF del endpoint de consulta electoral."""
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .esquema import documentar_consulta
from .serializers import ResultadoConsultaSerializer
from .services import consultar_por_cedula
from .validators import validar_cedula


class ConsultaRateThrottle(AnonRateThrottle):
    """Límite de consultas por IP (tasa 'consulta' en REST_FRAMEWORK) para evitar recorridos masivos de cédulas."""
    scope = 'consulta'


class ConsultaView(APIView):
    """
    POST /api/consulta/ con {"cedula": "..."}.

    La cédula va en el cuerpo y no en la URL para que no quede en logs ni
    historiales. Consulta pública: sin autenticación (y por lo tanto sin CSRF).
    Los errores los traduce exceptions.manejador_de_errores.
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [ConsultaRateThrottle]

    @documentar_consulta
    def post(self, request):
        """Valida la cédula, busca a la persona y devuelve su información electoral."""
        if not isinstance(request.data, dict):
            raise ParseError()
        cedula = validar_cedula(request.data.get('cedula'))
        persona = consultar_por_cedula(cedula)
        return Response(ResultadoConsultaSerializer(persona).data)
