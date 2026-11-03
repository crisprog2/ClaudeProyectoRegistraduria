"""Steps del feature consulta_lugar_votacion.feature (ejecutados contra la API)."""
from pytest_bdd import given, scenarios, then, when

from support.data_loader import caso
from support.edad import edad_esperada

scenarios('consulta_lugar_votacion.feature')


@given('un ciudadano registrado que no fue designado jurado', target_fixture='ciudadano')
def ciudadano_solo_votante():
    """Caso 'solo_votante' de tests/data/ciudadanos.json."""
    return caso('ciudadanos', 'solo_votante')


@when('consulta con su número de cédula rodeado de espacios', target_fixture='respuesta')
def consultar_con_espacios(api, ciudadano):
    """Consulta con la cédula precedida y seguida de espacios."""
    return api.consultar(f"  {ciudadano['cedula']}  ")


@then('ve su nombre completo y su edad')
def ve_nombre_y_edad(respuesta, ciudadano):
    """Nombre completo exacto y edad calculada con el oráculo de las pruebas."""
    datos = respuesta.json()['ciudadano']
    assert datos['nombre_completo'] == ciudadano['esperado']['ciudadano']['nombre_completo']
    assert datos['edad'] == edad_esperada(ciudadano['fecha_nacimiento'])


@then('se le informa que no tiene designación como jurado')
def no_tiene_designacion(respuesta):
    """En la API, la ausencia de designación es jurado = null."""
    assert respuesta.json()['jurado'] is None
