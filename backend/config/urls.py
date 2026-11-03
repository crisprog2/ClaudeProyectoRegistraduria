"""Enrutamiento raíz del proyecto: admin de Django y API bajo /api/."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.consultas.urls')),
]
