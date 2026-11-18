"""
Serializadores de la sesión.

Los docstrings de las clases se publican en Swagger: las notas internas van en
comentarios. El token de refresco nunca aparece aquí: viaja solo en la cookie.
"""
from rest_framework import serializers

from .roles import ROLES


class SolicitudIngresoSerializer(serializers.Serializer):
    """Credenciales para iniciar sesión."""
    # Solo documenta el cuerpo: la vista exige los dos campos con su propio error (DATOS_INCOMPLETOS).
    usuario = serializers.CharField(help_text='Nombre de usuario, p. ej. `analista.demo`.')
    contrasena = serializers.CharField(help_text='Contraseña del usuario.', style={'input_type': 'password'})


class UsuarioSesionSerializer(serializers.Serializer):
    """Usuario con sesión iniciada y su rol en la aplicación."""
    # Recibe un dict armado por la vista: {'usuario', 'nombre', 'rol'}.
    usuario = serializers.CharField(help_text='Nombre de usuario.')
    nombre = serializers.CharField(help_text='Nombre para mostrar; si no tiene, el nombre de usuario.')
    rol = serializers.ChoiceField(choices=ROLES, help_text='Rol en la aplicación.')


class RespuestaIngresoSerializer(serializers.Serializer):
    """Token de acceso y datos del usuario. El token de refresco va en la cookie, nunca aquí."""
    acceso = serializers.CharField(help_text='Token de acceso (JWT). Se envía en la cabecera `Authorization: Bearer <token>`.')
    tipo = serializers.CharField(help_text='Tipo de token para la cabecera Authorization: siempre `Bearer`.')
    expira_en = serializers.IntegerField(help_text='Segundos de vida del token de acceso (900 = 15 minutos).')
    usuario = UsuarioSesionSerializer()


def datos_usuario(usuario, rol):
    """Diccionario para UsuarioSesionSerializer."""
    return {'usuario': usuario.get_username(), 'nombre': usuario.get_full_name() or usuario.get_username(), 'rol': rol}


def datos_sesion(sesion):
    """Diccionario para RespuestaIngresoSerializer a partir de un services.Sesion."""
    return {
        'acceso': sesion.acceso,
        'tipo': 'Bearer',
        'expira_en': sesion.segundos_acceso,
        'usuario': datos_usuario(sesion.usuario, sesion.rol),
    }
