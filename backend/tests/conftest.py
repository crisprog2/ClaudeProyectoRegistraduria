"""
Fixtures del nivel backend (white-box).

Las pruebas corren contra MySQL (base test_registraduria, creada y borrada
por pytest-django) con los datos de demostración del fixture datos_demo.
Con --alluredir=, sus resultados aparecen como "Backend" en el reporte de Allure.
"""
from datetime import date

import allure
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.cuentas.roles import ANALISTA

# Fecha fija para que las edades esperadas no dependan del día de ejecución.
FECHA_REFERENCIA = date(2026, 11, 3)

# Contraseña de los usuarios que crean las pruebas. Solo existe en la base de pruebas,
# que pytest-django crea y borra en cada corrida; no es la de ningún usuario real ni demo.
CONTRASENA_PRUEBA = 'Clave-De-Prueba-2026'


@pytest.fixture
def datos_demo(db):
    """Carga el fixture datos_demo.json en la base de pruebas."""
    call_command('loaddata', 'datos_demo', verbosity=0)


@pytest.fixture(autouse=True)
def _grupo_allure():
    """Agrupa estas pruebas como "Backend" en el reporte de Allure (sin --alluredir no hace nada)."""
    allure.dynamic.parent_suite('Backend')


@pytest.fixture(autouse=True)
def limpiar_cache():
    """Reinicia el contador del límite de consultas (vive en la caché) entre pruebas."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def fecha_fija(monkeypatch):
    """Hace que timezone.localdate() devuelva FECHA_REFERENCIA."""
    monkeypatch.setattr(timezone, 'localdate', lambda *args, **kwargs: FECHA_REFERENCIA)


@pytest.fixture
def cliente():
    """Cliente HTTP de DRF."""
    return APIClient()


@pytest.fixture
def url_consulta():
    """URL del endpoint de consulta (/api/consulta/)."""
    return reverse('consultas:consulta')


@pytest.fixture
def crear_usuario(db):
    """
    Función que crea un usuario de prueba con CONTRASENA_PRUEBA.

    Por defecto es un analista activo. rol=None crea un usuario sin rol.
    """
    def _crear(usuario='usuario.prueba', rol=ANALISTA, activo=True, superusuario=False, staff=False):
        """Crea el usuario y, si se indica, lo agrega al grupo de su rol."""
        cuenta = get_user_model().objects.create_user(
            usuario, password=CONTRASENA_PRUEBA, first_name='Usuario', last_name='Prueba',
            is_active=activo, is_superuser=superusuario, is_staff=staff,
        )
        if rol:
            cuenta.groups.add(Group.objects.get(name=rol))
        return cuenta
    return _crear


@pytest.fixture
def ingresar(cliente):
    """Función que inicia sesión por la API; el cliente guarda la cookie del token de refresco."""
    def _ingresar(usuario='usuario.prueba', contrasena=CONTRASENA_PRUEBA, **extra):
        """POST a /api/auth/ingresar/; extra son cabeceras o atributos del request (p. ej. REMOTE_ADDR)."""
        return cliente.post(reverse('cuentas:ingresar'), {'usuario': usuario, 'contrasena': contrasena}, format='json', **extra)
    return _ingresar


@pytest.fixture
def cabecera_app():
    """Cabecera propia que exigen refrescar y salir, en el formato del cliente de pruebas de Django."""
    nombre, valor = settings.CABECERA_APP
    return {f'HTTP_{nombre.upper().replace("-", "_")}': valor}


@pytest.fixture
def consultar(cliente, url_consulta, datos_demo, fecha_fija):
    """Función que envía {"cedula": valor} al endpoint y devuelve la respuesta."""
    def _consultar(cedula, **extra):
        """Envía la cédula; extra son encabezados o atributos del request (p. ej. REMOTE_ADDR)."""
        return cliente.post(url_consulta, {'cedula': cedula}, format='json', **extra)
    return _consultar
