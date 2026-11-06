"""Steps compartidos entre features, ejecutados en el navegador con los Page Objects."""
from playwright.sync_api import expect
from pytest_bdd import parsers, then, when


@when('consulta con su número de cédula')
def consultar_con_su_cedula(consulta, ciudadano):
    """Abre la pantalla de consulta y envía la cédula del ciudadano elegido en el paso Dado."""
    consulta.consultar_hasta_resultado(ciudadano['cedula'])


@then('ve su puesto, dirección, ciudad, departamento y mesa de votación')
def ve_su_lugar_de_votacion(resultado, ciudadano):
    """La tarjeta "Tu lugar para votar" muestra los datos esperados, con la mesa en tres dígitos."""
    lugar = ciudadano['esperado']['lugar_votacion']
    tarjeta = resultado.tarjeta_votacion
    expect(resultado.valor_de(tarjeta, 'Puesto de votación')).to_have_text(lugar['puesto'])
    expect(resultado.valor_de(tarjeta, 'Dirección')).to_have_text(lugar['direccion'])
    expect(resultado.valor_de(tarjeta, 'Ciudad')).to_have_text(lugar['ciudad'])
    expect(resultado.valor_de(tarjeta, 'Departamento')).to_have_text(lugar['departamento'])
    assert resultado.numero_de_mesa(tarjeta) == f"{lugar['mesa']:03d}"


@then(parsers.parse('ve el mensaje "{mensaje}"'))
def ve_el_mensaje(consulta, mensaje):
    """
    La alerta contiene el mensaje del feature, sin su punto final: el feature usa el
    mensaje de la API y el panel del Figma muestra "No encontramos..." sin punto.
    """
    expect(consulta.alerta).to_contain_text(mensaje.rstrip('.'))
