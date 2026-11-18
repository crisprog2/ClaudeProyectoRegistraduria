"""
Crea los grupos de los roles de la aplicación: Administrador y Analista.

Es una migración de datos: no crea tablas (los grupos viven en auth_group, de Django).
Así los roles existen en cualquier base, la local, la del CI y la de pruebas, sin pasos
manuales. Los nombres se escriben aquí y no se importan de roles.py, porque una
migración debe seguir funcionando igual aunque el código cambie después.
"""
from django.db import migrations

GRUPOS = ('Administrador', 'Analista')


def crear_grupos(apps, schema_editor):
    """Crea los grupos si no existen."""
    Group = apps.get_model('auth', 'Group')
    for nombre in GRUPOS:
        Group.objects.get_or_create(name=nombre)


def borrar_grupos(apps, schema_editor):
    """Revierte la migración: borra los dos grupos."""
    apps.get_model('auth', 'Group').objects.filter(name__in=GRUPOS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(crear_grupos, borrar_grupos),
    ]
