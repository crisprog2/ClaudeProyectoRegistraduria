"""
Fixtures del nivel backend (white-box).

Las pruebas corren contra MySQL (base test_registraduria, creada y borrada
por pytest-django) con los datos de demostración del fixture datos_demo.
"""
from datetime import date

import pytest
from django.core.cache import cache
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

# Fecha fija para que las edades esperadas no dependan del día de ejecución.
FECHA_REFERENCIA = date(2026, 11, 3)


@pytest.fixture
def datos_demo(db):
    """Carga el fixture datos_demo.json en la base de pruebas."""
    call_command('loaddata', 'datos_demo', verbosity=0)


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
def consultar(cliente, url_consulta, datos_demo, fecha_fija):
    """Función que envía {"cedula": valor} al endpoint y devuelve la respuesta."""
    def _consultar(cedula, **extra):
        """Envía la cédula; extra son encabezados o atributos del request (p. ej. REMOTE_ADDR)."""
        return cliente.post(url_consulta, {'cedula': cedula}, format='json', **extra)
    return _consultar
