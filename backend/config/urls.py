"""Enrutamiento raíz del proyecto. Las URLs de la API se montarán bajo /api/ cuando exista el endpoint."""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
