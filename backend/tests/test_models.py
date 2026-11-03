"""Pruebas unitarias de las propiedades calculadas de Persona (no usan base de datos)."""
from datetime import date

import pytest

from apps.consultas.models import Persona


def persona(**campos):
    """Persona en memoria (sin guardar) con valores por defecto para los campos no indicados."""
    datos = {'primer_nombre': 'Ana', 'segundo_nombre': '', 'primer_apellido': 'Ruiz', 'segundo_apellido': '',
             'fecha_nacimiento': date(1990, 6, 15)}
    return Persona(**{**datos, **campos})


@pytest.mark.parametrize('segundo_nombre, segundo_apellido, esperado', [
    ('María', 'Gómez', 'Ana María Ruiz Gómez'),
    ('', 'Gómez', 'Ana Ruiz Gómez'),
    ('María', '', 'Ana María Ruiz'),
    ('', '', 'Ana Ruiz'),
])
def test_nombre_completo_omite_opcionales_vacios(segundo_nombre, segundo_apellido, esperado):
    assert persona(segundo_nombre=segundo_nombre, segundo_apellido=segundo_apellido).nombre_completo == esperado


@pytest.mark.parametrize('nacimiento, referencia, edad', [
    (date(1990, 6, 15), date(2026, 6, 14), 35),  # un día antes del cumpleaños
    (date(1990, 6, 15), date(2026, 6, 15), 36),  # el día del cumpleaños
    (date(2000, 2, 29), date(2026, 2, 28), 25),  # 29 de febrero en año no bisiesto: aún no cumple
    (date(2000, 2, 29), date(2026, 3, 1), 26),   # cumple el 1 de marzo
    (date(2000, 2, 29), date(2028, 2, 29), 28),  # año bisiesto: cumple el 29
    (date(2008, 1, 15), date(2026, 1, 15), 18),  # mayoría de edad exacta
])
def test_calcular_edad_en_dias_limite(nacimiento, referencia, edad):
    assert persona(fecha_nacimiento=nacimiento).calcular_edad(referencia) == edad
