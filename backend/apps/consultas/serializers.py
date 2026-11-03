"""
Serializadores de la respuesta de la consulta electoral.

Solo exponen lo que muestra la interfaz: nunca género, fecha de nacimiento
ni IDs internos. La cédula y la mesa salen sin formato; el frontend las
muestra como 1.098.765.432 y 018.
"""
from django.utils import timezone
from rest_framework import serializers


class UbicacionMesaSerializer(serializers.Serializer):
    """Mesa con su puesto, dirección, ciudad y departamento (recibe una Mesa)."""
    mesa = serializers.IntegerField(source='numero')
    puesto = serializers.CharField(source='puesto.nombre')
    direccion = serializers.CharField(source='puesto.direccion')
    ciudad = serializers.CharField(source='puesto.ciudad.nombre')
    departamento = serializers.CharField(source='puesto.ciudad.departamento.nombre')


class JuradoSerializer(serializers.Serializer):
    """Designación como jurado con la ubicación de su mesa de servicio (recibe una DesignacionJurado)."""
    rol = serializers.CharField()
    rol_display = serializers.CharField(source='get_rol_display')
    misma_mesa = serializers.SerializerMethodField()

    def get_misma_mesa(self, designacion):
        """True si presta servicio en la misma mesa donde vota."""
        return designacion.mesa_servicio_id == designacion.persona.mesa_id

    def to_representation(self, designacion):
        """Agrega mesa, puesto, dirección, ciudad y departamento de la mesa de servicio."""
        datos = super().to_representation(designacion)
        ubicacion = UbicacionMesaSerializer(designacion.mesa_servicio).data
        return {'rol': datos['rol'], 'rol_display': datos['rol_display'], **ubicacion, 'misma_mesa': datos['misma_mesa']}


class CiudadanoSerializer(serializers.Serializer):
    """Identificación de la persona consultada (recibe una Persona)."""
    cedula = serializers.CharField()
    nombre_completo = serializers.CharField()
    edad = serializers.SerializerMethodField()

    def get_edad(self, persona):
        """Edad en años cumplidos según la fecha local (America/Bogota)."""
        return persona.calcular_edad(timezone.localdate())


class ResultadoConsultaSerializer(serializers.Serializer):
    """Respuesta completa: ciudadano, lugar de votación y jurado (null si es solo votante)."""
    ciudadano = CiudadanoSerializer(source='*')
    lugar_votacion = UbicacionMesaSerializer(source='mesa')
    jurado = serializers.SerializerMethodField()

    def get_jurado(self, persona):
        """Designación como jurado o None si la persona es solo votante."""
        designacion = getattr(persona, 'designacion_jurado', None)
        return JuradoSerializer(designacion).data if designacion else None
