"""
Pruebas black-box de la documentación de la API: que Swagger diga la verdad.

Comparan la especificación publicada en /api/schema/ con las respuestas reales
de los mismos casos de tests/data/ que usa el resto de la suite. El 429 no se
puede provocar aquí sin agotar el límite: se comprueba en backend/tests/.
"""
import re
from urllib.parse import urljoin, urlparse

import pytest

from support.api_client import RUTA_CONSULTA, RUTA_DOCUMENTACION, RUTA_ESQUEMA
from support.data_loader import cargar, como_parametros

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_especificacion_se_publica_en_json_y_yaml(api):
    json_ = api.obtener(RUTA_ESQUEMA, params={'format': 'json'})
    yaml = api.obtener(RUTA_ESQUEMA)

    assert json_.status_code == 200
    assert json_.json()['info']['title'] == 'ConsultaVoto API'
    assert yaml.status_code == 200
    assert yaml.text.startswith('openapi: 3.1.0')


def test_solo_documenta_el_post_de_consulta(especificacion):
    assert {ruta: list(metodos) for ruta, metodos in especificacion.contenido['paths'].items()} == {RUTA_CONSULTA: ['post']}


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
