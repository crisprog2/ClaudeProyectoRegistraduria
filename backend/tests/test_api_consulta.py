"""Pruebas del endpoint POST /api/consulta/: respuestas, errores y límite de consultas."""
import pytest

UBICACION_ESPERANZA = {
    'puesto': 'Colegio Cívico La Esperanza',
    'direccion': 'Calle 48 # 65-20',
    'ciudad': 'Medellín',
    'departamento': 'Antioquia',
}


def test_jurado_en_la_misma_mesa_caso_figma(consultar):
    respuesta = consultar('1098765432')
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        'ciudadano': {'cedula': '1098765432', 'nombre_completo': 'Carlos Andrés Martínez', 'edad': 36},
        'lugar_votacion': {'mesa': 18, **UBICACION_ESPERANZA},
        'jurado': {'rol': 'TITULAR', 'rol_display': 'Jurado titular', 'mesa': 18, **UBICACION_ESPERANZA, 'misma_mesa': True},
    }


def test_solo_votante_caso_figma(consultar):
    respuesta = consultar('1023456789')
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        'ciudadano': {'cedula': '1023456789', 'nombre_completo': 'Laura Camila Gómez', 'edad': 32},
        'lugar_votacion': {'mesa': 12, **UBICACION_ESPERANZA},
        'jurado': None,
    }


def test_jurado_en_otra_mesa_del_mismo_puesto(consultar):
    datos = consultar('1017234568').json()
    assert datos['lugar_votacion']['mesa'] == 17
    assert datos['jurado']['mesa'] == 19 and datos['jurado']['rol'] == 'REMANENTE'
    assert datos['jurado']['misma_mesa'] is False


def test_jurado_en_otro_puesto(consultar):
    datos = consultar('1036845120').json()
    assert datos['lugar_votacion']['puesto'] == 'Colegio Cívico La Esperanza'
    assert datos['jurado']['puesto'] == 'Institución Educativa Los Almendros'
    assert datos['jurado']['mesa'] == 5 and datos['jurado']['misma_mesa'] is False


def test_cedula_con_espacios_externos_se_acepta(consultar):
    respuesta = consultar('  1098765432  ')
    assert respuesta.status_code == 200
    assert respuesta.json()['ciudadano']['cedula'] == '1098765432'


def test_nombre_sin_segundo_nombre(consultar):
    assert consultar('1017234568').json()['ciudadano']['nombre_completo'] == 'Juliana Muñoz Restrepo'


@pytest.mark.parametrize('cedula', ['1098765432', '1023456789'])
def test_no_expone_datos_innecesarios(consultar, cedula):
    datos = consultar(cedula).json()
    assert set(datos['ciudadano']) == {'cedula', 'nombre_completo', 'edad'}
    texto = str(datos)
    for campo in ('genero', 'fecha_nacimiento', 'cod_mesa', 'cod_puesto', 'cod_designacion'):
        assert campo not in texto


@pytest.mark.parametrize('cuerpo', [{'cedula': ''}, {'cedula': '   '}, {'cedula': None}, {}])
def test_cedula_requerida(cliente, url_consulta, datos_demo, cuerpo):
    respuesta = cliente.post(url_consulta, cuerpo, format='json')
    assert respuesta.status_code == 400
    assert respuesta.json() == {'codigo': 'CEDULA_REQUERIDA', 'mensaje': 'Ingresa tu número de cédula para consultar.'}


@pytest.mark.parametrize('cedula', ['1.023.456.789', '1023 456789', '10234a6789', '12345', '10987654321', '0123456789', 1098765432])
def test_formato_invalido(consultar, cedula):
    respuesta = consultar(cedula)
    assert respuesta.status_code == 400
    assert respuesta.json() == {
        'codigo': 'CEDULA_FORMATO_INVALIDO',
        'mensaje': 'El número no es válido. Escribe solo números, sin puntos, espacios ni comas.',
    }


def test_cedula_no_encontrada(consultar):
    respuesta = consultar('1000000000')
    assert respuesta.status_code == 404
    assert respuesta.json() == {'codigo': 'CEDULA_NO_ENCONTRADA', 'mensaje': 'No encontramos información para esta cédula.'}


@pytest.mark.parametrize('metodo', ['get', 'put', 'patch', 'delete'])
def test_solo_acepta_post(cliente, url_consulta, metodo):
    respuesta = getattr(cliente, metodo)(url_consulta)
    assert respuesta.status_code == 405
    assert respuesta.json()['codigo'] == 'METODO_NO_PERMITIDO'


@pytest.mark.parametrize('cuerpo, tipo, status_esperado', [
    ('{"cedula": ', 'application/json', 400),        # JSON mal formado
    ('["1098765432"]', 'application/json', 400),     # JSON válido pero no es un objeto
    ('cedula=1098765432', 'application/x-www-form-urlencoded', 415),
])
def test_solicitud_invalida(cliente, url_consulta, cuerpo, tipo, status_esperado):
    respuesta = cliente.post(url_consulta, cuerpo, content_type=tipo)
    assert respuesta.status_code == status_esperado
    assert respuesta.json()['codigo'] == 'SOLICITUD_INVALIDA'


def test_limite_de_consultas_por_ip(consultar):
    for _ in range(30):
        assert consultar('1098765432').status_code == 200
    respuesta = consultar('1098765432')
    assert respuesta.status_code == 429
    assert respuesta.json()['codigo'] == 'DEMASIADAS_CONSULTAS'
    assert 'Retry-After' in respuesta.headers


def test_x_forwarded_for_no_evade_el_limite(consultar):
    """Cambiar la cabecera X-Forwarded-For no debe reiniciar el límite (NUM_PROXIES = 0)."""
    for _ in range(30):
        consultar('1098765432')
    respuesta = consultar('1098765432', HTTP_X_FORWARDED_FOR='203.0.113.7')
    assert respuesta.status_code == 429


def test_no_requiere_csrf(datos_demo, fecha_fija, url_consulta):
    """La consulta es pública: funciona aunque el cliente aplique la verificación CSRF."""
    from rest_framework.test import APIClient
    respuesta = APIClient(enforce_csrf_checks=True).post(url_consulta, {'cedula': '1098765432'}, format='json')
    assert respuesta.status_code == 200
