"""Pruebas white-box de la configuración: variables de entorno y controlador de MySQL."""
import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db import connection

from config.settings.base import env_bool, env_entero_positivo, env_requerida


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


@pytest.mark.parametrize('valor', [None, ''], ids=['ausente', 'vacia'])
def test_variable_obligatoria_sin_valor_detiene_el_arranque(monkeypatch, valor):
    """Sin la clave de Django o los datos de MySQL, la app no debe arrancar con valores vacíos."""
    if valor is None:
        monkeypatch.delenv('VARIABLE_DE_PRUEBA', raising=False)
    else:
        monkeypatch.setenv('VARIABLE_DE_PRUEBA', valor)

    with pytest.raises(ImproperlyConfigured, match="Falta la variable de entorno obligatoria 'VARIABLE_DE_PRUEBA'"):
        env_requerida('VARIABLE_DE_PRUEBA')


def test_variable_obligatoria_con_valor(monkeypatch):
    monkeypatch.setenv('VARIABLE_DE_PRUEBA', 'valor')

    assert env_requerida('VARIABLE_DE_PRUEBA') == 'valor'


@pytest.mark.parametrize('valor, esperado', [('45', 45), ('', 30), ('  ', 30), (' 7 ', 7)])
def test_entero_positivo_valido_o_valor_por_defecto(monkeypatch, valor, esperado):
    monkeypatch.setenv('VARIABLE_DE_PRUEBA', valor)

    assert env_entero_positivo('VARIABLE_DE_PRUEBA', 30) == esperado


@pytest.mark.parametrize('valor', ['0', '00', '-5', '1.5', 'abc', '10/min'])
def test_entero_positivo_invalido_detiene_el_arranque(monkeypatch, valor):
    """Un límite de consultas mal escrito no debe dejar la API sin límite ni con uno inesperado."""
    monkeypatch.setenv('VARIABLE_DE_PRUEBA', valor)

    with pytest.raises(ImproperlyConfigured, match='debe ser un entero mayor que 0'):
        env_entero_positivo('VARIABLE_DE_PRUEBA', 30)


def test_la_conexion_usa_pymysql(db):
    """mysqlclient queda fuera: su componente compilado lo bloquea Windows (ver config/__init__.py)."""
    connection.ensure_connection()

    assert type(connection.connection).__module__.startswith('pymysql')
