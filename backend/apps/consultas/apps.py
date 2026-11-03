"""Configuración de la app de dominio 'consultas'."""
from django.apps import AppConfig


class ConsultasConfig(AppConfig):
    """App con el modelo de datos, la lógica y la API de la consulta electoral."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.consultas'
    label = 'consultas'
    verbose_name = 'Consultas electorales'
