"""
Pruebas white-box del admin de Django.

El admin sirve para revisar los datos de demostración. Estas pruebas abren cada
listado con un superusuario de prueba (fixture admin_client de pytest-django,
que solo existe en la base de pruebas) y verifican la lógica propia del admin:
el filtro "es jurado", las columnas calculadas y que el listado de personas no
haga una consulta por fila.
"""
import pytest
from django.contrib import admin
from django.urls import reverse

from apps.consultas.admin import DesignacionJuradoAdmin, PersonaAdmin
from apps.consultas.models import Ciudad, Departamento, DesignacionJurado, Mesa, Persona, PuestoVotacion

JURADOS = {'1098765432', '1143987654', '1017234568', '52748193', '1036845120'}
SOLO_VOTANTES = {'1023456789', '1144056789', '79563214', '1095827364', '4567891'}
MODELOS = [Departamento, Ciudad, PuestoVotacion, Mesa, Persona, DesignacionJurado]


def url_listado(modelo):
    """URL del listado del modelo en el admin, p. ej. /admin/consultas/persona/."""
    return reverse(f'admin:consultas_{modelo._meta.model_name}_changelist')


def cedulas_listadas(respuesta):
    """Cédulas de las personas que muestra el listado (todas las páginas)."""
    return {persona.cedula for persona in respuesta.context['cl'].queryset}


@pytest.mark.parametrize('modelo', MODELOS, ids=lambda modelo: modelo.__name__)
def test_el_listado_de_cada_modelo_abre(admin_client, datos_demo, modelo):
    respuesta = admin_client.get(url_listado(modelo))

    assert respuesta.status_code == 200


def test_la_ficha_de_una_persona_abre_con_su_designacion(admin_client, datos_demo):
    """La ficha incluye la edad calculada (solo lectura) y la designación como jurado (inline)."""
    respuesta = admin_client.get(reverse('admin:consultas_persona_change', args=['1098765432']))

    assert respuesta.status_code == 200
    assert 'designacion_jurado' in respuesta.content.decode()


@pytest.mark.parametrize('valor, esperadas', [
    ('si', JURADOS),
    ('no', SOLO_VOTANTES),
    (None, JURADOS | SOLO_VOTANTES),
], ids=['jurados', 'solo-votantes', 'sin-filtro'])
def test_filtro_es_jurado(admin_client, datos_demo, valor, esperadas):
    parametros = {'es_jurado': valor} if valor else {}

    respuesta = admin_client.get(url_listado(Persona), parametros)

    assert cedulas_listadas(respuesta) == esperadas


@pytest.mark.parametrize('cedula, es_jurado', [('1098765432', True), ('1023456789', False)])
def test_columna_es_jurado(datos_demo, cedula, es_jurado):
    columnas = PersonaAdmin(Persona, admin.site)

    assert columnas.es_jurado(Persona.objects.get(pk=cedula)) is es_jurado


@pytest.mark.parametrize('cedula, misma_mesa', [
    ('1098765432', True),   # jurado en la misma mesa donde vota
    ('1017234568', False),  # otra mesa del mismo puesto
    ('1036845120', False),  # otro puesto
])
def test_columna_vota_en_la_misma_mesa(datos_demo, cedula, misma_mesa):
    columnas = DesignacionJuradoAdmin(DesignacionJurado, admin.site)

    assert columnas.misma_mesa(DesignacionJurado.objects.get(persona=cedula)) is misma_mesa


def test_el_listado_de_personas_no_hace_una_consulta_por_fila(admin_client, datos_demo, django_assert_max_num_queries):
    """
    PersonaAdmin.list_select_related trae la designación de jurado junto con el listado.

    Medido el 2026-11-17: con list_select_related, el listado hace 6 consultas (sesión,
    usuario, conteos, filtros y la lista). Sin él, 16: una más por cada una de las 10
    personas, por la columna "Es jurado". El límite de 8 deja margen para el admin y
    falla mucho antes de una consulta por fila.

    Solo se prueba Persona: en los demás listados, Django ya aplica select_related a
    las ForeignKey de list_display aunque no se declare. La designación es una relación
    inversa (OneToOne desde DesignacionJurado) y Django no la incluye por su cuenta.
    """
    with django_assert_max_num_queries(8):
        admin_client.get(url_listado(Persona))
