"""Steps compartidos entre features: consultar con la cédula del ciudadano, ver el lugar de votación y ver un mensaje."""
from pytest_bdd import parsers, then, when


@when('consulta con su número de cédula', target_fixture='respuesta')
def consultar_con_su_cedula(api, ciudadano):
    """Consulta con la cédula del ciudadano elegido en el paso Dado."""
    return api.consultar(ciudadano['cedula'])


@then('ve su puesto, dirección, ciudad, departamento y mesa de votación')
def ve_su_lugar_de_votacion(respuesta, ciudadano):
    """El lugar de votación coincide exactamente con el esperado para el ciudadano."""
    assert respuesta.status_code == 200
    assert respuesta.json()['lugar_votacion'] == ciudadano['esperado']['lugar_votacion']


@then(parsers.parse('ve el mensaje "{mensaje}"'))
def ve_el_mensaje(respuesta, mensaje):
    """La consulta fue rechazada con el mensaje indicado."""
    assert respuesta.status_code >= 400
    assert respuesta.json()['mensaje'] == mensaje
