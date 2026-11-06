"""Enrutamiento raíz del proyecto: admin de Django, API bajo /api/ y su documentación."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='esquema-api'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='esquema-api'), name='documentacion-api'),
    path('api/', include('apps.consultas.urls')),
]
