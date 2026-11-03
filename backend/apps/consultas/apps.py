from django.apps import AppConfig


class ConsultasConfig(AppConfig):
    """Configuración de la app de dominio 'consultas'."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.consultas'
    label = 'consultas'
    verbose_name = 'Consultas electorales'
