"""Pruebas de la lógica de consulta: escenarios del fixture, cédula no registrada y número de consultas SQL."""
import pytest

from apps.consultas.services import CedulaNoEncontrada, consultar_por_cedula


def es_jurado(persona):
    """True si la persona tiene una designación como jurado."""
    return hasattr(persona, 'designacion_jurado')


@pytest.mark.parametrize('cedula', ['1023456789', '1144056789', '79563214', '1095827364', '4567891'])
def test_solo_votante_no_tiene_designacion(datos_demo, cedula):
    assert not es_jurado(consultar_por_cedula(cedula))


@pytest.mark.parametrize('cedula', ['1098765432', '1143987654'])
def test_jurado_en_la_misma_mesa(datos_demo, cedula):
    persona = consultar_por_cedula(cedula)
    assert persona.designacion_jurado.mesa_servicio_id == persona.mesa_id


@pytest.mark.parametrize('cedula', ['1017234568', '52748193'])
def test_jurado_en_otra_mesa_del_mismo_puesto(datos_demo, cedula):
    persona = consultar_por_cedula(cedula)
    servicio = persona.designacion_jurado.mesa_servicio
    assert servicio.pk != persona.mesa_id and servicio.puesto_id == persona.mesa.puesto_id


def test_jurado_en_otro_puesto(datos_demo):
    persona = consultar_por_cedula('1036845120')
    assert persona.designacion_jurado.mesa_servicio.puesto_id != persona.mesa.puesto_id


def test_cedula_no_registrada(datos_demo):
    with pytest.raises(CedulaNoEncontrada):
        consultar_por_cedula('1000000000')


@pytest.mark.parametrize('cedula', ['1098765432', '1023456789'])
def test_trae_todo_en_una_sola_consulta_sql(datos_demo, django_assert_num_queries, cedula):
    """Persona, mesa, puesto, ciudad, departamento y designación se leen en 1 consulta."""
    with django_assert_num_queries(1):
        persona = consultar_por_cedula(cedula)
        persona.mesa.puesto.ciudad.departamento.nombre
        designacion = getattr(persona, 'designacion_jurado', None)
        if designacion:
            designacion.mesa_servicio.puesto.ciudad.departamento.nombre
