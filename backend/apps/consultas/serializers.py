"""
Serializadores de la respuesta de la consulta electoral.

Solo exponen lo que muestra la interfaz: nunca género, fecha de nacimiento
ni IDs internos. La cédula y la mesa salen sin formato; el frontend las
muestra como 1.098.765.432 y 018.
"""
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import DesignacionJurado


class UbicacionMesaSerializer(serializers.Serializer):
    """Mesa con su puesto, dirección, ciudad y departamento."""
    # Recibe una Mesa. El docstring se publica en Swagger.
    mesa = serializers.IntegerField(source='numero', help_text='Número de mesa, sin ceros a la izquierda.')
    puesto = serializers.CharField(source='puesto.nombre')
    direccion = serializers.CharField(source='puesto.direccion')
    ciudad = serializers.CharField(source='puesto.ciudad.nombre')
    departamento = serializers.CharField(source='puesto.ciudad.departamento.nombre')


class JuradoSerializer(serializers.Serializer):
    """Designación como jurado con la ubicación de su mesa de servicio."""
    # Recibe una DesignacionJurado.
    rol = serializers.ChoiceField(choices=DesignacionJurado.Rol.choices)
    rol_display = serializers.CharField(source='get_rol_display', help_text='Nombre del rol para mostrar.')
    mesa = serializers.IntegerField(source='mesa_servicio.numero', help_text='Número de la mesa de servicio.')
    puesto = serializers.CharField(source='mesa_servicio.puesto.nombre')
    direccion = serializers.CharField(source='mesa_servicio.puesto.direccion')
    ciudad = serializers.CharField(source='mesa_servicio.puesto.ciudad.nombre')
    departamento = serializers.CharField(source='mesa_servicio.puesto.ciudad.departamento.nombre')
    misma_mesa = serializers.SerializerMethodField(help_text='Indica si presta servicio en la misma mesa donde vota.')

    def get_misma_mesa(self, designacion) -> bool:
        """True si presta servicio en la misma mesa donde vota."""
        return designacion.mesa_servicio_id == designacion.persona.mesa_id


class CiudadanoSerializer(serializers.Serializer):
    """Identificación de la persona consultada."""
    # Recibe una Persona.
    cedula = serializers.CharField(help_text='Solo dígitos, sin puntos.')
    nombre_completo = serializers.CharField()
    edad = serializers.SerializerMethodField(help_text='Años cumplidos a la fecha de la consulta.')

    def get_edad(self, persona) -> int:
        """Edad en años cumplidos según la fecha local (America/Bogota)."""
        return persona.calcular_edad(timezone.localdate())


class ResultadoConsultaSerializer(serializers.Serializer):
    """Respuesta completa: ciudadano, lugar de votación y jurado (null si es solo votante)."""
    ciudadano = CiudadanoSerializer(source='*')
    lugar_votacion = UbicacionMesaSerializer(source='mesa')
    jurado = serializers.SerializerMethodField(help_text='Asignación como jurado; `null` si es solo votante.')

    @extend_schema_field(JuradoSerializer(allow_null=True))
    def get_jurado(self, persona):
        """Designación como jurado o None si la persona es solo votante."""
        designacion = getattr(persona, 'designacion_jurado', None)
        return JuradoSerializer(designacion).data if designacion else None
