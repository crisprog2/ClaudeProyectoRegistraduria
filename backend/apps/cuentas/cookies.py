"""
Cookie del token de refresco.

Atributos (configuración en settings.JWT_COOKIE; motivos en docs/decisiones/0002):
- HttpOnly: JavaScript no puede leerla. Si alguien lograra inyectar código en la página
  (XSS), no podría llevarse el token de refresco.
- SameSite=Strict: el navegador no la envía en peticiones que vienen de otro sitio.
- Path=/api/auth/: solo viaja a refrescar y salir, no en cada petición de la API.
- Max-Age: lo que le queda de vida al token, para que la cookie no lo sobreviva.
- Secure (JWT_COOKIE_SECURE): solo por HTTPS. Apagado en local y en el CI, que usan http://.
"""
from django.conf import settings


def _configuracion():
    """Configuración vigente de la cookie (se lee en cada llamada para respetar override_settings)."""
    return settings.JWT_COOKIE


def leer_cookie_refresco(request):
    """Texto del token de refresco que envió el navegador, o None."""
    return request.COOKIES.get(_configuracion()['NOMBRE'])


def poner_cookie_refresco(respuesta, token, segundos):
    """Guarda el token de refresco en la cookie, con una duración de `segundos`."""
    cookie = _configuracion()
    respuesta.set_cookie(
        cookie['NOMBRE'], str(token), max_age=segundos, path=cookie['RUTA'],
        httponly=True, samesite=cookie['SAMESITE'], secure=cookie['SECURE'],
    )


def borrar_cookie_refresco(respuesta):
    """Le indica al navegador que borre la cookie (misma ruta y SameSite con que se creó)."""
    cookie = _configuracion()
    respuesta.delete_cookie(cookie['NOMBRE'], path=cookie['RUTA'], samesite=cookie['SAMESITE'])
