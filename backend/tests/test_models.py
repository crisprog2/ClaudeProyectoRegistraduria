"""
Pruebas del modelo de datos.

- Propiedades calculadas de Persona: en memoria, sin base de datos.
- Textos de __str__: con los datos de demostración, porque leen modelos relacionados.
  Son los que muestra el admin y los que documenta CLAUDE.md.
"""
from datetime import date

import pytest

from apps.consultas.models import Ciudad, Departamento, DesignacionJurado, Mesa, Persona, PuestoVotacion


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


def test_edad_es_la_edad_a_la_fecha_de_hoy():
    ana = persona(fecha_nacimiento=date(1990, 6, 15))

    assert ana.edad == ana.calcular_edad(date.today())


@pytest.mark.parametrize('obtener, esperado', [
    (lambda: Departamento.objects.get(pk='05'), 'Antioquia'),
    (lambda: Ciudad.objects.get(pk='05001'), 'Medellín'),
    (lambda: PuestoVotacion.objects.get(pk='050010101'), 'Colegio Cívico La Esperanza - Calle 48 # 65-20'),
    (lambda: Mesa.objects.get(puesto='050010101', numero=18), 'Mesa 018 · Colegio Cívico La Esperanza'),
    (lambda: Persona.objects.get(pk='1098765432'), 'Carlos Martínez'),
    (lambda: DesignacionJurado.objects.get(persona='1098765432'),
     'Jurado titular · Carlos Martínez · Mesa 018 · Colegio Cívico La Esperanza'),
], ids=['departamento', 'ciudad', 'puesto', 'mesa', 'persona', 'designacion'])
def test_str_legible_sin_ids_internos(datos_demo, obtener, esperado):
    assert str(obtener()) == esperado
