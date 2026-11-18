"""Enrutamiento raíz del proyecto: admin de Django, API bajo /api/, sesión bajo /api/auth/ y documentación."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='esquema-api'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='esquema-api'), name='documentacion-api'),
    # Antes que 'api/': la ruta /api/auth/ es también la ruta de la cookie del token de refresco.
    path('api/auth/', include('apps.cuentas.urls')),
    path('api/', include('apps.consultas.urls')),
]
