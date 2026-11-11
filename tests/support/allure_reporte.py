"""
Plugin de pytest que organiza el reporte de Allure de las pruebas black-box.

Se registra en tests/conftest.py y solo actúa cuando pytest corre con
--alluredir; sin esa opción, allure-pytest no guarda nada y este plugin no
cambia el resultado de ninguna prueba.

- Agrupa las pruebas por nivel (API, BDD, E2E) y los escenarios BDD por canal
  (API o interfaz) y por feature, porque los mismos features corren dos veces.
- Registra cada paso de Gherkin como un paso del reporte. Se hace con los hooks
  de pytest-bdd porque allure-pytest-bdd no puede instalarse junto a
  allure-pytest: los dos registran la opción --alluredir.
- Marca como críticas las pruebas smoke.
- Si una prueba falla, adjunta la evidencia: la última petición y respuesta de
  la API y, en las pruebas de interfaz, la captura, la URL y la traza de
  Playwright.
- Escribe environment.properties con versiones y URLs, sin secretos.
"""
import json
import platform
from importlib import metadata
from pathlib import Path

import allure
import pytest

from support import config

GRUPOS = {'api': 'API', 'bdd': 'BDD', 'e2e': 'E2E'}
CANALES_BDD = {'api': 'Por la API', 'interfaz': 'Por la interfaz'}
# pytest-playwright guarda aquí su registro de artefactos y lo borra en el reporte de desmontaje.
ATRIBUTO_ARTEFACTOS_PLAYWRIGHT = '_playwright_artifacts_recorder'
PAQUETES_DEL_ENTORNO = ('pytest', 'pytest-bdd', 'playwright', 'allure-pytest', 'requests')


def _carpetas(item):
    """Carpetas de la prueba relativas a la raíz, p. ej. ('tests', 'bdd', 'step_defs', 'api')."""
    return Path(item.path).relative_to(item.config.rootpath).parts[:-1]


@pytest.fixture(autouse=True)
def _etiquetas_allure(request):
    """Nivel de la prueba como grupo principal del reporte y severidad crítica para las smoke."""
    carpetas = _carpetas(request.node)
    nivel = carpetas[1] if len(carpetas) > 1 else ''
    allure.dynamic.parent_suite(GRUPOS.get(nivel, 'Otras'))
    if nivel == 'bdd':
        allure.dynamic.suite(CANALES_BDD.get(carpetas[-1], carpetas[-1]))
    if request.node.get_closest_marker('smoke'):
        allure.dynamic.severity(allure.severity_level.CRITICAL)


@pytest.hookimpl
def pytest_bdd_before_scenario(request, feature, scenario):
    """Título, feature y descripción del escenario; los ejemplos del esquema, como parámetros legibles."""
    allure.dynamic.title(scenario.name)
    allure.dynamic.feature(feature.name)
    allure.dynamic.story(scenario.name)
    allure.dynamic.sub_suite(feature.name)
    # Sin esto, Allure muestra el docstring que genera pytest-bdd, con la ruta del archivo en el disco.
    allure.dynamic.description(feature.description or feature.name)
    # Cada columna del ejemplo como parámetro propio. El parámetro interno _pytest_bdd_example
    # lo quita reportes/preparar-resultados.mjs, porque Allure 3 no respeta el modo oculto.
    for nombre, valor in (request.node.funcargs.get('_pytest_bdd_example') or {}).items():
        allure.dynamic.parameter(nombre, valor)


@pytest.hookimpl
def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    """Abre un paso del reporte con el texto del paso de Gherkin."""
    paso = allure.step(f'{step.keyword} {step.name}')
    paso.__enter__()
    request.node._paso_allure = paso


@pytest.hookimpl
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    """Cierra el paso como exitoso."""
    request.node._paso_allure.__exit__(None, None, None)


@pytest.hookimpl
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """Cierra el paso con el error para que el reporte señale en qué paso falló."""
    request.node._paso_allure.__exit__(type(exception), exception, exception.__traceback__)


def _adjuntar_peticion_api(api):
    """Adjunta la última petición enviada a la API y su respuesta."""
    respuesta = api.ultima_respuesta
    if respuesta is None:
        return
    peticion = respuesta.request
    cuerpo = peticion.body.decode('utf-8', 'replace') if isinstance(peticion.body, bytes) else peticion.body
    allure.attach(
        f'{peticion.method} {peticion.url}\nContent-Type: {peticion.headers.get("Content-Type", "")}\n\n{cuerpo or ""}',
        name='Petición a la API', attachment_type=allure.attachment_type.TEXT,
    )
    try:
        contenido = json.dumps(respuesta.json(), ensure_ascii=False, indent=2)
        tipo = allure.attachment_type.JSON
    except ValueError:
        contenido, tipo = respuesta.text, allure.attachment_type.TEXT
    allure.attach(contenido, name=f'Respuesta de la API ({respuesta.status_code})', attachment_type=tipo)


def _adjuntar_pagina(page):
    """Adjunta la URL y una captura de la página tal como quedó al fallar."""
    if page.is_closed():
        return
    allure.attach(page.url, name='URL de la página', attachment_type=allure.attachment_type.URI_LIST)
    allure.attach(page.screenshot(full_page=True), name='Captura al fallar', attachment_type=allure.attachment_type.PNG)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """El cliente de la API dura toda la sesión: se olvida la respuesta de la prueba anterior."""
    if item.funcargs.get('api') is not None:
        item.funcargs['api'].ultima_respuesta = None
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Adjunta la evidencia de una prueba fallida y, al final, la traza de Playwright si se guardó."""
    registro_playwright = getattr(item, ATRIBUTO_ARTEFACTOS_PLAYWRIGHT, None)
    resultado = yield
    reporte = resultado.get_result()

    if reporte.when == 'call' and reporte.failed:
        if item.funcargs.get('api') is not None:
            _adjuntar_peticion_api(item.funcargs['api'])
        if item.funcargs.get('page') is not None:
            _adjuntar_pagina(item.funcargs['page'])

    if reporte.when == 'teardown' and registro_playwright is not None:
        for tipo, ruta in registro_playwright.artifacts:
            if tipo == 'trace':
                allure.attach.file(ruta, name='Traza de Playwright (abrir en trace.playwright.dev)', extension='zip')


def _version(paquete):
    """Versión instalada de un paquete de Python, o 'no instalado'."""
    try:
        return metadata.version(paquete)
    except metadata.PackageNotFoundError:
        return 'no instalado'


def pytest_sessionfinish(session):
    """Escribe environment.properties en la carpeta de resultados de Allure."""
    carpeta = session.config.getoption('--alluredir', default=None)
    if not carpeta:
        return
    navegadores = session.config.getoption('--browser', default=None) or ['chromium']
    datos = {
        'Python': platform.python_version(),
        'Sistema': f'{platform.system()} {platform.version()}',
        **{paquete: _version(paquete) for paquete in PAQUETES_DEL_ENTORNO},
        'Navegadores': ', '.join(navegadores),
        'API': config.API_BASE_URL,
        'Frontend': config.FRONTEND_BASE_URL,
    }
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    lineas = [f'{clave.replace(" ", "_")}={valor}' for clave, valor in datos.items()]
    (Path(carpeta) / 'environment.properties').write_text('\n'.join(lineas) + '\n', encoding='utf-8')
