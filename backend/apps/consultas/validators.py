"""
Reglas de validación del número de cédula.

No dependen de DRF: lanzan django.core.exceptions.ValidationError con un
código estable (CEDULA_REQUERIDA o CEDULA_FORMATO_INVALIDO) que el
manejador de errores de la API traduce a la respuesta {codigo, mensaje}.
"""
import re

from django.core.exceptions import ValidationError

CEDULA_REQUERIDA = 'CEDULA_REQUERIDA'
CEDULA_FORMATO_INVALIDO = 'CEDULA_FORMATO_INVALIDO'

MENSAJES = {
    CEDULA_REQUERIDA: 'Ingresa tu número de cédula para consultar.',
    CEDULA_FORMATO_INVALIDO: 'El número no es válido. Escribe solo números, sin puntos, espacios ni comas.',
}

# De 6 a 10 dígitos ASCII, sin cero inicial. Se usa [0-9] y no \d para no
# aceptar dígitos Unicode de otros alfabetos (p. ej. dígitos de ancho completo).
PATRON_CEDULA = re.compile(r'[1-9][0-9]{5,9}')


def _error(codigo):
    """ValidationError con el mensaje del Figma correspondiente al código."""
    return ValidationError(MENSAJES[codigo], code=codigo)


def validar_cedula(valor):
    """
    Normaliza y valida una cédula. Devuelve la cédula limpia como texto.

    - Quita los espacios al inicio y al final (error común al copiar y pegar).
    - None, texto vacío o solo espacios -> CEDULA_REQUERIDA.
    - Valores que no son texto (p. ej. un número JSON), espacios internos,
      puntos, comas, letras, cero inicial o longitud fuera de 6-10 dígitos
      -> CEDULA_FORMATO_INVALIDO.
    """
    if valor is None:
        raise _error(CEDULA_REQUERIDA)
    if not isinstance(valor, str):
        raise _error(CEDULA_FORMATO_INVALIDO)
    cedula = valor.strip()
    if not cedula:
        raise _error(CEDULA_REQUERIDA)
    if not PATRON_CEDULA.fullmatch(cedula):
        raise _error(CEDULA_FORMATO_INVALIDO)
    return cedula
