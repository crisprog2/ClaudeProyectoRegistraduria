"""
Lógica de la sesión: iniciar, renovar y cerrar.

Las vistas solo traducen HTTP; las reglas viven aquí:
- Solo inicia sesión un usuario activo, que no sea superusuario y que tenga un rol.
  Cualquier otro caso da el mismo error (CredencialesInvalidas).
- Cada renovación revoca el token de refresco anterior (rotación). El nuevo conserva
  el vencimiento del original: la sesión dura como máximo 8 horas desde que se inició.
- Cerrar sesión revoca el token de refresco. El token de acceso ya entregado sigue
  siendo válido hasta que vence (15 minutos como máximo): es el costo de que no se
  guarde en el servidor (ver docs/decisiones/0002).
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .excepciones import CredencialesInvalidas, SesionExpirada
from .roles import rol_de


@dataclass
class Sesion:
    """Tokens emitidos para un usuario: el de acceso va en el JSON y el de refresco en la cookie."""
    usuario: object
    rol: str
    acceso: str
    refresco: RefreshToken

    @property
    def segundos_acceso(self):
        """Vida del token de acceso, en segundos (para el campo expira_en)."""
        return int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds())

    @property
    def segundos_refresco(self):
        """Lo que le queda de vida al token de refresco, en segundos (Max-Age de la cookie)."""
        vence = datetime.fromtimestamp(self.refresco['exp'], tz=timezone.utc)
        return max(0, int((vence - datetime.now(tz=timezone.utc)).total_seconds()))


def iniciar_sesion(request, usuario, contrasena):
    """Comprueba las credenciales y el rol, y emite los tokens. Lanza CredencialesInvalidas."""
    cuenta = authenticate(request, username=usuario, password=contrasena)
    rol = rol_de(cuenta)
    if rol is None:
        raise CredencialesInvalidas()
    refresco = RefreshToken.for_user(cuenta)
    return Sesion(cuenta, rol, str(refresco.access_token), refresco)


def renovar_sesion(texto_refresco):
    """
    Revoca el token de refresco recibido y emite uno nuevo con el mismo vencimiento.

    Lanza SesionExpirada si el token falta, es inválido, venció o ya fue revocado, o si
    su usuario ya no existe, está inactivo o perdió el rol. En ese caso también lo revoca.
    """
    refresco = _validar(texto_refresco)
    usuario = get_user_model().objects.filter(**{api_settings.USER_ID_FIELD: refresco[api_settings.USER_ID_CLAIM]}).first()
    rol = rol_de(usuario)
    refresco.blacklist()
    if rol is None:
        raise SesionExpirada()
    # Mismo procedimiento que la rotación de simplejwt, pero sin set_exp(): conserva el vencimiento.
    refresco.set_jti()
    refresco.set_iat()
    refresco.outstand()
    return Sesion(usuario, rol, str(refresco.access_token), refresco)


def cerrar_sesion(texto_refresco):
    """Revoca el token de refresco si es válido. No falla si ya no lo era: cerrar sesión siempre funciona."""
    try:
        _validar(texto_refresco).blacklist()
    except SesionExpirada:
        pass


def _validar(texto_refresco):
    """RefreshToken verificado (firma, tipo, vencimiento y lista de revocados) o SesionExpirada."""
    if not texto_refresco:
        raise SesionExpirada()
    try:
        return RefreshToken(texto_refresco)
    except TokenError as error:
        raise SesionExpirada() from error
