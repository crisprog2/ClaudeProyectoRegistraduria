"""Rutas de la API de consultas (montadas bajo /api/ en config/urls.py)."""
from django.urls import path

from .views import ConsultaView

app_name = 'consultas'

urlpatterns = [
    path('consulta/', ConsultaView.as_view(), name='consulta'),
]
