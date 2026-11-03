"""Pruebas unitarias de las reglas de validación de cédula (no usan base de datos)."""
import pytest
from django.core.exceptions import ValidationError

from apps.consultas.validators import CEDULA_FORMATO_INVALIDO, CEDULA_REQUERIDA, validar_cedula


@pytest.mark.parametrize('valor, esperado', [
    ('123456', '123456'),            # mínimo: 6 dígitos
    ('4567891', '4567891'),          # cédula antigua de 7 dígitos
    ('79563214', '79563214'),        # cédula antigua de 8 dígitos
    ('1098765432', '1098765432'),    # cédula actual de 10 dígitos
    (' 1098765432 ', '1098765432'),  # espacios al inicio y al final (copiar y pegar)
    ('\t1098765432\n', '1098765432'),
])
def test_cedulas_validas_se_normalizan(valor, esperado):
    assert validar_cedula(valor) == esperado


@pytest.mark.parametrize('valor', [None, '', '   ', '\t\n'])
def test_cedula_vacia_es_requerida(valor):
    with pytest.raises(ValidationError) as error:
        validar_cedula(valor)
    assert error.value.code == CEDULA_REQUERIDA


@pytest.mark.parametrize('valor', [
    '1.023.456.789',   # puntos
    '1,023,456,789',   # comas
    '1023 456789',     # espacio interno
    '10234a6789',      # letra
    'abcdefghij',
    '12345',           # 5 dígitos
    '10987654321',     # 11 dígitos
    '0123456789',      # cero inicial
    '-123456',         # signo
    '+1098765432',
    '１０９８７６５４３２',  # dígitos de ancho completo (Unicode)
    1098765432,        # número en vez de texto
    True,
    ['1098765432'],
])
def test_formatos_invalidos(valor):
    with pytest.raises(ValidationError) as error:
        validar_cedula(valor)
    assert error.value.code == CEDULA_FORMATO_INVALIDO
