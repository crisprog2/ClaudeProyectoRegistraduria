"""
Pruebas black-box de la documentación de la API: que Swagger diga la verdad.

Comparan la especificación publicada en /api/schema/ con las respuestas reales
de los mismos casos de tests/data/ que usa el resto de la suite. El 429 no se
puede provocar aquí sin agotar el límite: se comprueba en backend/tests/.

Cubre la consulta (POST /api/consulta/) y, al final, las rutas de la sesión (/api/auth/).
"""
import re
from urllib.parse import urljoin, urlparse

import pytest

from support.api_client import RUTA_CONSULTA, RUTA_DOCUMENTACION, RUTA_ESQUEMA
from support.data_loader import cargar, caso, como_parametros
from support.sesion_client import RUTAS as RUTAS_SESION
from support.sesion_client import SESION

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_especificacion_se_publica_en_json_y_yaml(api):
    json_ = api.obtener(RUTA_ESQUEMA, params={'format': 'json'})
    yaml = api.obtener(RUTA_ESQUEMA)

    assert json_.status_code == 200
    assert json_.json()['info']['title'] == 'ConsultaVoto API'
    assert yaml.status_code == 200
    assert yaml.text.startswith('openapi: 3.1.0')


def test_documenta_la_consulta_y_las_rutas_de_la_sesion(especificacion):
    esperadas = {RUTA_CONSULTA: ['post']}
    for nombre, ruta in RUTAS_SESION.items():
        esperadas[ruta] = [SESION['metodo_permitido'][nombre].lower()]

    assert {ruta: list(metodos) for ruta, metodos in especificacion.contenido['paths'].items()} == esperadas


def test_documenta_todos_los_codigos_http(especificacion):
    assert especificacion.codigos_http == {200, 400, 404, 405, 415, 429}


def test_la_cedula_es_obligatoria_en_el_cuerpo(especificacion):
    assert especificacion.operacion['requestBody']['required'] is True
    assert especificacion.contenido['components']['schemas']['SolicitudConsulta']['required'] == ['cedula']


def test_campos_documentados_coinciden_con_el_contrato(especificacion, contrato):
    assert especificacion.propiedades('ResultadoConsulta') == set(contrato['claves_raiz'])
    assert especificacion.propiedades('Ciudadano') == set(contrato['claves_ciudadano'])
    assert especificacion.propiedades('UbicacionMesa') == set(contrato['claves_lugar_votacion'])
    assert especificacion.propiedades('Jurado') == set(contrato['claves_jurado'])


def test_no_documenta_datos_sensibles(especificacion, contrato):
    componentes = ('ResultadoConsulta', 'Ciudadano', 'UbicacionMesa', 'Jurado')
    documentados = set().union(*(especificacion.propiedades(componente) for componente in componentes))

    assert not documentados & set(contrato['claves_prohibidas'])


@pytest.mark.parametrize('ciudadano', como_parametros('ciudadanos'))
def test_respuesta_exitosa_cumple_el_esquema(api, especificacion, ciudadano):
    respuesta = api.consultar(ciudadano['cedula'])

    assert respuesta.status_code == 200
    assert especificacion.errores_de_validacion(200, respuesta.json()) == []


def afirmar_error_documentado(especificacion, respuesta):
    """El código HTTP, el cuerpo y el código de error real están en la documentación."""
    http = respuesta.status_code
    assert http in especificacion.codigos_http
    assert especificacion.errores_de_validacion(http, respuesta.json()) == []
    assert respuesta.json()['codigo'] in {ejemplo['codigo'] for ejemplo in especificacion.ejemplos_respuesta(http)}


@pytest.mark.parametrize('caso', como_parametros('cedulas_invalidas'))
def test_error_de_cedula_cumple_el_esquema(api, especificacion, caso):
    afirmar_error_documentado(especificacion, api.enviar_json(caso['cuerpo']))


@pytest.mark.parametrize('solicitud', como_parametros('solicitudes_invalidas'))
def test_error_de_protocolo_cumple_el_esquema(api, especificacion, solicitud):
    afirmar_error_documentado(especificacion, api.enviar_solicitud(solicitud))


def test_ejemplos_exitosos_son_lo_que_responde_la_api(api, especificacion):
    """La edad cambia con la fecha, así que se compara todo lo demás y se valida su tipo con el esquema."""
    ejemplos = especificacion.ejemplos_respuesta(200)
    assert ejemplos

    for ejemplo in ejemplos:
        assert especificacion.errores_de_validacion(200, ejemplo) == []
        real = api.consultar(ejemplo['ciudadano']['cedula']).json()
        real['ciudadano']['edad'] = ejemplo['ciudadano']['edad']
        assert ejemplo == real


def test_ejemplos_de_error_usan_los_mensajes_reales(especificacion, mensajes_error):
    for http in especificacion.codigos_http - {200}:
        ejemplos = especificacion.ejemplos_respuesta(http)
        assert ejemplos, f'El código {http} no tiene ejemplos'
        for ejemplo in ejemplos:
            assert ejemplo['mensaje'] == mensajes_error[ejemplo['codigo']]


def test_ejemplos_de_solicitud_responden_lo_que_prometen(api, especificacion):
    ejemplos = especificacion.ejemplos_solicitud()
    assert ejemplos

    for ejemplo in ejemplos:
        respuesta = api.enviar_json(ejemplo['value'])
        assert f'Responde {respuesta.status_code}' in ejemplo['description']


def test_documentacion_no_menciona_entidades_reales(api):
    texto = api.obtener(RUTA_ESQUEMA, params={'format': 'json'}).text.lower()

    for frase in cargar('textos_interfaz')['frases_prohibidas']:
        assert frase.lower() not in texto


def test_documentacion_avisa_que_los_datos_son_ficticios(especificacion):
    assert 'ficticia' in especificacion.contenido['info']['description']
    assert 'ficticios' in especificacion.operacion['description']


@pytest.mark.smoke
def test_swagger_ui_responde(api):
    respuesta = api.obtener(RUTA_DOCUMENTACION)

    assert respuesta.status_code == 200
    assert respuesta.headers['Content-Type'].startswith('text/html')


def test_swagger_ui_carga_sus_archivos_desde_el_proyecto(api):
    """Sin CDN: cada archivo que pide la página vive en este servidor y responde."""
    pagina = api.obtener(RUTA_DOCUMENTACION)
    archivos = [urljoin(pagina.url, ruta) for ruta in re.findall(r'(?:src|href)="([^"]+)"', pagina.text)]

    assert any('swagger-ui-bundle' in archivo for archivo in archivos)
    for archivo in archivos:
        assert urlparse(archivo).netloc == urlparse(api.base_url).netloc
        assert api.obtener(archivo).status_code == 200, archivo


# --- Sesión (/api/auth/) -------------------------------------------------------------------

def _operacion(especificacion, nombre):
    """Especificación de una ruta de la sesión por su nombre en tests/data/sesion.json."""
    return especificacion.de(RUTAS_SESION[nombre], SESION['metodo_permitido'][nombre])


def _respuestas_reales_de_la_sesion(cliente):
    """(nombre de la ruta, respuesta) de un recorrido por todos los casos de la sesión."""
    analista = caso('usuarios', 'analista')
    respuestas = [
        ('ingresar', cliente.enviar_ingreso(caso('credenciales_invalidas', 'contrasena_incorrecta')['cuerpo'])),
        ('ingresar', cliente.enviar_ingreso(caso('credenciales_invalidas', 'cuerpo_vacio')['cuerpo'])),
        ('refrescar', cliente.refrescar()),
        ('sesion', cliente.ver_sesion()),
        ('sesion', cliente.ver_sesion('token-invalido')),
    ]
    acceso = cliente.ingresar_como(analista)
    respuestas += [
        ('ingresar', acceso),
        ('sesion', cliente.ver_sesion(acceso.json()['acceso'])),
        ('refrescar', cliente.refrescar(con_cabecera=False)),
        ('refrescar', cliente.refrescar()),
        ('salir', cliente.salir(con_cabecera=False)),
    ]
    respuestas += [(nombre, cliente.pedir('GET' if metodo == 'POST' else 'POST', nombre, headers=cabeceras))
                   for nombre, metodo, cabeceras in (
                       ('ingresar', 'POST', {}), ('refrescar', 'POST', {}), ('salir', 'POST', {}),
                       ('sesion', 'GET', {'Authorization': f'Bearer {acceso.json()["acceso"]}'}))]
    return respuestas


def test_respuestas_reales_de_la_sesion_cumplen_el_esquema(cliente_sesion, especificacion):
    for nombre, respuesta in _respuestas_reales_de_la_sesion(cliente_sesion):
        operacion = _operacion(especificacion, nombre)
        http = respuesta.status_code
        assert http in operacion.codigos_http, (nombre, http)
        assert operacion.errores_de_validacion(http, respuesta.json()) == [], (nombre, http)
        if http >= 400:
            assert respuesta.json()['codigo'] in {ejemplo['codigo'] for ejemplo in operacion.ejemplos_respuesta(http)}


def test_salir_documenta_el_204(cliente_sesion, especificacion):
    assert 204 in _operacion(especificacion, 'salir').codigos_http
    assert cliente_sesion.salir().status_code == 204


def test_ejemplos_de_error_de_la_sesion_usan_los_mensajes_reales(especificacion, mensajes_error):
    for nombre in RUTAS_SESION:
        operacion = _operacion(especificacion, nombre)
        for http in {codigo for codigo in operacion.codigos_http if codigo >= 400}:
            for ejemplo in operacion.ejemplos_respuesta(http):
                esperado = (SESION['mensaje_metodo_no_permitido'][SESION['metodo_permitido'][nombre]]
                            if ejemplo['codigo'] == 'METODO_NO_PERMITIDO' else mensajes_error[ejemplo['codigo']])
                assert ejemplo['mensaje'] == esperado, (nombre, http, ejemplo['codigo'])


def test_la_respuesta_de_ingreso_no_documenta_el_token_de_refresco(especificacion):
    assert especificacion.propiedades('RespuestaIngreso') == set(SESION['claves_respuesta_ingreso'])
    assert especificacion.propiedades('UsuarioSesion') == set(SESION['claves_usuario'])


def test_solo_la_ruta_de_sesion_exige_token(especificacion):
    esquemas = especificacion.contenido['components']['securitySchemes']
    assert esquemas['jwtAuth'] == {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}

    for nombre in RUTAS_SESION:
        seguridad = _operacion(especificacion, nombre).operacion['security']
        assert seguridad == ([{'jwtAuth': []}] if nombre == 'sesion' else [{}]), nombre
    assert especificacion.operacion['security'] == [{}]


def test_documenta_la_cookie_y_la_cabecera_de_la_aplicacion(especificacion):
    assert 'Set-Cookie' in _operacion(especificacion, 'ingresar').cabeceras_respuesta(200)
    assert 'Retry-After' in _operacion(especificacion, 'ingresar').cabeceras_respuesta(429)
    for nombre in ('refrescar', 'salir'):
        parametros = {(p['name'], p['in']): p for p in _operacion(especificacion, nombre).operacion['parameters']}
        cabecera = parametros[(SESION['cabecera_app']['nombre'], 'header')]
        assert cabecera['required'] is True
        assert cabecera['schema']['enum'] == [SESION['cabecera_app']['valor']]
        assert (SESION['cookie']['nombre'], 'cookie') in parametros
