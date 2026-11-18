"""Rutas de la sesión (montadas bajo /api/auth/ en config/urls.py, la ruta de la cookie)."""
from django.urls import path

from .views import IngresarView, RefrescarView, SalirView, SesionView

app_name = 'cuentas'

urlpatterns = [
    path('ingresar/', IngresarView.as_view(), name='ingresar'),
    path('refrescar/', RefrescarView.as_view(), name='refrescar'),
    path('salir/', SalirView.as_view(), name='salir'),
    path('sesion/', SesionView.as_view(), name='sesion'),
]
