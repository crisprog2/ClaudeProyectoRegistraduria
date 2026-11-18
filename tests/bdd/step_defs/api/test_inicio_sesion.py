"""
Steps del feature inicio_sesion.feature (ejecutados contra la API).

El estado viaja en fixtures con target_fixture: 'usuario_demo' (caso de
tests/data/usuarios.json), 'respuesta' (respuesta HTTP) y 'cookie_anterior'. La
cookie de la sesión la guarda el fixture cliente_sesion, nuevo en cada escenario.
El canal de interfaz se agrega en la fase 5, cuando exista la pantalla de inicio de sesión.
"""
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from support.data_loader import cargar, caso

pytestmark = pytest.mark.api

scenarios('inicio_sesion.feature')


def usuario_con_rol(rol):
    """Caso de tests/data/usuarios.json cuyo rol esperado es `rol`."""
    return next(usuario for usuario in cargar('usuarios') if usuario['esperado']['rol'] == rol)


@given(parsers.parse('el usuario de demostración con rol "{rol}"'), target_fixture='usuario_demo')
def usuario_de_demostracion(rol):
    """Usuario de demostración del rol indicado."""
    return usuario_con_rol(rol)


@given(parsers.parse('que el usuario con rol "{rol}" inició sesión'), target_fixture='usuario_demo')
def usuario_con_sesion_iniciada(cliente_sesion, rol):
    """Inicia sesión con el usuario de demostración del rol; el cliente guarda la cookie."""
    usuario = usuario_con_rol(rol)
    assert cliente_sesion.ingresar_como(usuario).status_code == 200
    return usuario


@when('inicia sesión con su contraseña', target_fixture='respuesta')
def iniciar_sesion(cliente_sesion, usuario_demo):
    """Inicia sesión con la contraseña del .env."""
    return cliente_sesion.ingresar_como(usuario_demo)


@when('inicia sesión con una contraseña incorrecta', target_fixture='respuesta')
def iniciar_sesion_con_contrasena_incorrecta(cliente_sesion, usuario_demo):
    """Usuario correcto, contraseña del caso 'contrasena_incorrecta'."""
    contrasena = caso('credenciales_invalidas', 'contrasena_incorrecta')['cuerpo']['contrasena']
    return cliente_sesion.ingresar(usuario_demo['usuario'], contrasena)


@when('inicia sesión con un usuario que no existe', target_fixture='respuesta')
def iniciar_sesion_con_usuario_inexistente(cliente_sesion):
    """Credenciales del caso 'usuario_inexistente'."""
    return cliente_sesion.enviar_ingreso(caso('credenciales_invalidas', 'usuario_inexistente')['cuerpo'])


@when('inicia sesión sin escribir el usuario ni la contraseña', target_fixture='respuesta')
def iniciar_sesion_sin_datos(cliente_sesion):
    """Usuario y contraseña vacíos."""
    return cliente_sesion.enviar_ingreso(caso('credenciales_invalidas', 'textos_vacios')['cuerpo'])


@when('su acceso se renueva', target_fixture='respuesta')
def renovar_acceso(cliente_sesion):
    """Renueva el token de acceso con la cookie, como hará el frontend antes de que venza."""
    return cliente_sesion.refrescar()


@when('cierra sesión', target_fixture='cookie_anterior')
def cerrar_sesion(cliente_sesion):
    """Cierra la sesión y guarda la cookie que tenía, para comprobar después que quedó revocada."""
    anterior = cliente_sesion.cookie_refresco
    assert cliente_sesion.salir().status_code == 204
    return anterior


@then(parsers.parse('entra a la aplicación con el rol "{rol}"'))
@then(parsers.parse('sigue en la aplicación con el rol "{rol}"'))
def tiene_sesion_con_el_rol(cliente_sesion, respuesta, rol):
    """La respuesta trae un token de acceso, y ese token abre la sesión con el rol indicado."""
    assert respuesta.status_code == 200
    assert respuesta.json()['usuario']['rol'] == rol
    assert cliente_sesion.ver_sesion(respuesta.json()['acceso']).json()['rol'] == rol


@then('no entra a la aplicación')
def no_entra(cliente_sesion, respuesta):
    """Ni token de acceso en la respuesta ni cookie de sesión en el cliente."""
    assert 'acceso' not in respuesta.json()
    assert cliente_sesion.cookie_refresco is None


@then('su sesión ya no se puede renovar')
def sesion_revocada(cliente_sesion, cookie_anterior):
    """Ni siquiera con la cookie que tenía antes de salir: quedó revocada en el servidor."""
    cliente_sesion.poner_cookie_refresco(cookie_anterior)

    respuesta = cliente_sesion.refrescar()

    assert respuesta.status_code == 401
    assert respuesta.json()['codigo'] == 'SESION_EXPIRADA'
