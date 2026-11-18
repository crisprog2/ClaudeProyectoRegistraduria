"""
Comando: python manage.py crear_usuarios_demo

Crea o actualiza los usuarios de demostración, uno por rol:
- admin.demo (Administrador), con la contraseña de DEMO_ADMIN_CONTRASENA.
- analista.demo (Analista), con la contraseña de DEMO_ANALISTA_CONTRASENA.

Las contraseñas solo se leen de variables de entorno (el .env en local, el YAML en el
CI): nunca están en el código. Deben cumplir los validadores de Django. Se puede correr
varias veces: deja los usuarios activos, con su rol, su contraseña actual y sin acceso
al admin de Django (is_staff e is_superuser en False).
"""
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.cuentas.roles import ADMINISTRADOR, ANALISTA

# (usuario, nombre, apellido, rol, variable de entorno de la contraseña). Datos ficticios.
USUARIOS_DEMO = (
    ('admin.demo', 'Administrador', 'Demo', ADMINISTRADOR, 'DEMO_ADMIN_CONTRASENA'),
    ('analista.demo', 'Analista', 'Demo', ANALISTA, 'DEMO_ANALISTA_CONTRASENA'),
)


class Command(BaseCommand):
    """Crea o actualiza admin.demo y analista.demo."""
    help = 'Crea o actualiza los usuarios de demostración (contraseñas en DEMO_ADMIN_CONTRASENA y DEMO_ANALISTA_CONTRASENA).'

    def handle(self, *args, **options):
        """Valida todas las contraseñas antes de tocar la base y luego crea o actualiza los usuarios."""
        contrasenas = {variable: self._contrasena(usuario, variable) for usuario, *_, variable in USUARIOS_DEMO}
        with transaction.atomic():
            for usuario, nombre, apellido, rol, variable in USUARIOS_DEMO:
                creado = self._guardar(usuario, nombre, apellido, rol, contrasenas[variable])
                self.stdout.write(f'{"Creado" if creado else "Actualizado"}: {usuario} ({rol})')

    @staticmethod
    def _contrasena(usuario, variable):
        """Contraseña de la variable de entorno, validada con las reglas de Django. Nunca la muestra."""
        contrasena = os.environ.get(variable, '')
        if not contrasena:
            raise CommandError(f'Falta la variable de entorno {variable} (contraseña de {usuario}). Agrégala a tu .env.')
        try:
            validate_password(contrasena, user=get_user_model()(username=usuario))
        except ValidationError as error:
            raise CommandError(f'La contraseña de {variable} no cumple las reglas: {" ".join(error.messages)}') from error
        return contrasena

    @staticmethod
    def _guardar(usuario, nombre, apellido, rol, contrasena):
        """Crea o actualiza el usuario con un solo rol. Devuelve True si lo creó."""
        cuenta, creado = get_user_model().objects.get_or_create(username=usuario)
        cuenta.first_name, cuenta.last_name = nombre, apellido
        cuenta.is_active, cuenta.is_staff, cuenta.is_superuser = True, False, False
        cuenta.set_password(contrasena)
        cuenta.save()
        cuenta.groups.set([Group.objects.get(name=rol)])
        return creado
