"""Pruebas white-box de la configuración: variables de entorno y controlador de MySQL."""
import pytest
from django.db import connection

from config.settings.base import env_bool


@pytest.mark.parametrize('valor', ['', '   '])
@pytest.mark.parametrize('por_defecto', [True, False])
def test_variable_vacia_usa_el_valor_por_defecto(monkeypatch, valor, por_defecto):
    """Copiar .env.example deja DJANGO_DEBUG vacía: debe valer lo mismo que si no estuviera."""
    monkeypatch.setenv('VARIABLE_DE_PRUEBA', valor)

    assert env_bool('VARIABLE_DE_PRUEBA', por_defecto=por_defecto) is por_defecto


def test_variable_ausente_usa_el_valor_por_defecto(monkeypatch):
    monkeypatch.delenv('VARIABLE_DE_PRUEBA', raising=False)

    assert env_bool('VARIABLE_DE_PRUEBA', por_defecto=True) is True


@pytest.mark.parametrize('valor', ['1', 'true', 'TRUE', 'yes', 'si', 'sí'])
def test_valores_verdaderos(monkeypatch, valor):
    monkeypatch.setenv('VARIABLE_DE_PRUEBA', valor)

    assert env_bool('VARIABLE_DE_PRUEBA') is True


@pytest.mark.parametrize('valor', ['0', 'false', 'no'])
def test_valor_explicito_gana_sobre_el_valor_por_defecto(monkeypatch, valor):
    monkeypatch.setenv('VARIABLE_DE_PRUEBA', valor)

    assert env_bool('VARIABLE_DE_PRUEBA', por_defecto=True) is False


def test_la_conexion_usa_pymysql(db):
    """mysqlclient queda fuera: su componente compilado lo bloquea Windows (ver config/__init__.py)."""
    connection.ensure_connection()

    assert type(connection.connection).__module__.startswith('pymysql')
