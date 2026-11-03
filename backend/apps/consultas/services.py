"""Lógica de negocio de la consulta por cédula, separada de las vistas."""
from .models import Persona

CEDULA_NO_ENCONTRADA = 'CEDULA_NO_ENCONTRADA'


class CedulaNoEncontrada(Exception):
    """La cédula tiene formato válido pero no está registrada."""
    codigo = CEDULA_NO_ENCONTRADA
    mensaje = 'No encontramos información para esta cédula.'


def consultar_por_cedula(cedula):
    """
    Devuelve la Persona con su mesa de votación y, si existe, su designación
    como jurado, en una sola consulta SQL.

    La cédula debe llegar ya validada (ver validators.validar_cedula).
    Lanza CedulaNoEncontrada si no existe.
    """
    try:
        return Persona.objects.select_related(
            'mesa__puesto__ciudad__departamento',
            'designacion_jurado__mesa_servicio__puesto__ciudad__departamento',
        ).get(pk=cedula)
    except Persona.DoesNotExist:
        raise CedulaNoEncontrada() from None
