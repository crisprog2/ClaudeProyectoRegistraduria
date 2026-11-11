"""
Corre las suites de pruebas de ConsultaVoto con un solo comando.

Es la lógica común del CI: GitHub Actions lo llama desde .github/workflows/ci.yml,
y un Jenkinsfile o cualquier otra herramienta podría llamarlo igual. También sirve
en local, en lugar de abrir una terminal por servidor.

    python scripts/pruebas.py base                     # migraciones y datos de demostración
    python scripts/pruebas.py backend                  # white-box (pytest-django)
    python scripts/pruebas.py api                      # API y BDD por la API
    python scripts/pruebas.py interfaz --browser firefox
    python scripts/pruebas.py todo --allure            # backend, api e interfaz seguidos

Los comandos api, interfaz y todo levantan los servidores que necesitan, esperan a
que respondan y los apagan al terminar, aunque las pruebas fallen o se interrumpa
la corrida. El código de salida es el de pytest: 0 si todo pasó.

Usa el intérprete con el que se ejecuta (el del .venv) y solo la biblioteca
estándar y python-dotenv, que ya está en los requirements.
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import ExitStack, contextmanager
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]
BACKEND = RAIZ / 'backend'
FRONTEND = RAIZ / 'frontend'
RESULTADOS_ALLURE = RAIZ / 'reportes' / 'allure-results'
LOGS = RAIZ / 'reportes' / 'logs'

load_dotenv(RAIZ / '.env')
API_BASE_URL = (os.environ.get('API_BASE_URL') or 'http://127.0.0.1:8000').rstrip('/')
FRONTEND_BASE_URL = (os.environ.get('FRONTEND_BASE_URL') or 'http://localhost:5173').rstrip('/')

# La suite black-box hace muchas consultas seguidas: con el límite normal (30/min) recibiría 429.
LIMITE_CONSULTAS_PRUEBAS = '1000'
ESPERA_MAXIMA_SEGUNDOS = 90
NAVEGADORES = ('chromium', 'firefox', 'webkit')


def avisar(mensaje):
    """Imprime un mensaje del script, distinguible de la salida de pytest."""
    print(f'\n[pruebas] {mensaje}', flush=True)


def responde(url):
    """True si hay un servidor HTTP en la URL, sin importar el código de estado."""
    try:
        urllib.request.urlopen(url, timeout=2)
    except urllib.error.HTTPError:
        return True
    except (urllib.error.URLError, OSError):
        return False
    return True


def detener(proceso):
    """Detiene el proceso y sus hijos: npm deja a Vite como proceso hijo."""
    if proceso.poll() is not None:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(proceso.pid)], capture_output=True)
    else:
        os.killpg(proceso.pid, signal.SIGTERM)
    try:
        proceso.wait(timeout=15)
    except subprocess.TimeoutExpired:
        if os.name != 'nt':
            os.killpg(proceso.pid, signal.SIGKILL)
        proceso.wait()


def ultimas_lineas(ruta, cantidad=40):
    """Final de un log, para explicar por qué un servidor no arrancó."""
    lineas = ruta.read_text(encoding='utf-8', errors='replace').splitlines()
    return '\n'.join(lineas[-cantidad:])


@contextmanager
def servidor(nombre, comando, cwd, url, entorno=None):
    """
    Levanta un servidor, espera a que responda en la URL y lo detiene al salir.

    Si la URL ya responde, se detiene: otro servidor ocupa el puerto y las pruebas
    correrían contra él (por ejemplo, un backend con el límite normal de consultas).
    """
    if responde(url):
        raise SystemExit(
            f'Ya hay un servidor en {url}. Detenlo antes de correr las pruebas: '
            f'este script levanta su propio {nombre} con la configuración de pruebas.'
        )
    LOGS.mkdir(parents=True, exist_ok=True)
    ruta_log = LOGS / f'{nombre}.log'
    opciones = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True}
    with open(ruta_log, 'w', encoding='utf-8') as log:
        avisar(f'Levantando {nombre} en {url} (log: {ruta_log.relative_to(RAIZ)})')
        proceso = subprocess.Popen(
            comando, cwd=cwd, env={**os.environ, **(entorno or {})},
            stdout=log, stderr=subprocess.STDOUT, **opciones,
        )
        try:
            limite = time.monotonic() + ESPERA_MAXIMA_SEGUNDOS
            while not responde(url):
                if proceso.poll() is not None or time.monotonic() > limite:
                    log.flush()
                    raise SystemExit(f'El {nombre} no arrancó. Últimas líneas del log:\n{ultimas_lineas(ruta_log)}')
                time.sleep(0.5)
            yield
        finally:
            detener(proceso)
            avisar(f'{nombre} detenido')


def backend_en_marcha():
    """Servidor de Django con el límite de consultas alto que necesitan las pruebas black-box."""
    puerto = urlparse(API_BASE_URL).port or 8000
    host = urlparse(API_BASE_URL).hostname or '127.0.0.1'
    return servidor(
        'backend', [sys.executable, 'manage.py', 'runserver', f'{host}:{puerto}', '--noreload'],
        BACKEND, API_BASE_URL + '/api/schema/', {'CONSULTA_LIMITE_POR_MINUTO': LIMITE_CONSULTAS_PRUEBAS},
    )


def frontend_en_marcha():
    """Servidor de desarrollo de Vite, que reenvía /api al backend."""
    npm = shutil.which('npm')
    if npm is None:
        raise SystemExit('No se encontró npm. Instala Node.js para correr las pruebas de interfaz.')
    return servidor('frontend', [npm, 'run', 'dev'], FRONTEND, FRONTEND_BASE_URL)


def pytest(argumentos, cwd=RAIZ):
    """Corre pytest con el mismo intérprete y devuelve su código de salida."""
    comando = [sys.executable, '-m', 'pytest', *argumentos]
    avisar(f'{" ".join(comando[1:])}  (en {Path(cwd).relative_to(RAIZ) or "."})')
    return subprocess.run(comando, cwd=cwd).returncode


def opciones_allure(args, limpiar=False):
    """Argumentos de allure-pytest. --alluredir= va con signo igual: ver el README, paso 9."""
    if not args.allure:
        return []
    opciones = [f'--alluredir={RESULTADOS_ALLURE}']
    return opciones + ['--clean-alluredir'] if limpiar else opciones


def comando_base(args):
    """Aplica las migraciones y carga los datos de demostración (sobrescribe los registros del fixture)."""
    for argumentos in (['migrate', '--noinput'], ['loaddata', 'datos_demo']):
        avisar(f'manage.py {" ".join(argumentos)}')
        codigo = subprocess.run([sys.executable, 'manage.py', *argumentos], cwd=BACKEND).returncode
        if codigo:
            return codigo
    return 0


def comando_backend(args, limpiar=None):
    """Pruebas white-box del backend; no necesitan servidores."""
    limpiar = args.limpiar_allure if limpiar is None else limpiar
    return pytest(opciones_allure(args, limpiar), cwd=BACKEND)


def comando_api(args):
    """Pruebas de API y escenarios BDD por la API, con el backend en marcha."""
    with backend_en_marcha():
        return pytest(['tests', '-m', 'api', *opciones_allure(args, args.limpiar_allure)])


def comando_interfaz(args):
    """Escenarios BDD por la interfaz y E2E, con el backend y el frontend en marcha."""
    navegadores = [opcion for navegador in args.browser for opcion in ('--browser', navegador)]
    traza = ['--tracing', 'retain-on-failure'] if args.allure else []
    with ExitStack() as servidores:
        servidores.enter_context(backend_en_marcha())
        servidores.enter_context(frontend_en_marcha())
        return pytest(['tests', '-m', 'e2e', *navegadores, *traza, *opciones_allure(args, args.limpiar_allure)])


def comando_todo(args):
    """Backend, API e interfaz seguidos. Sigue aunque una suite falle, para tener el reporte completo."""
    codigos = {'backend': comando_backend(args, limpiar=True)}
    args.limpiar_allure = False
    with ExitStack() as servidores:
        servidores.enter_context(backend_en_marcha())
        codigos['api'] = pytest(['tests', '-m', 'api', *opciones_allure(args)])
        servidores.enter_context(frontend_en_marcha())
        navegadores = [opcion for navegador in args.browser for opcion in ('--browser', navegador)]
        traza = ['--tracing', 'retain-on-failure'] if args.allure else []
        codigos['interfaz'] = pytest(['tests', '-m', 'e2e', *navegadores, *traza, *opciones_allure(args)])
    avisar('Resumen: ' + ', '.join(f'{suite} {"pasó" if codigo == 0 else "FALLÓ"}' for suite, codigo in codigos.items()))
    if args.allure:
        avisar('Para ver el reporte: cd reportes; npm run reporte')
    return max(codigos.values())


def crear_parser():
    """Comandos y opciones de la línea de comandos."""
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0].strip(), formatter_class=argparse.RawDescriptionHelpFormatter)
    comandos = parser.add_subparsers(dest='comando', required=True)
    for nombre, funcion, ayuda in (
        ('base', comando_base, 'migraciones y datos de demostración'),
        ('backend', comando_backend, 'pruebas white-box del backend'),
        ('api', comando_api, 'API y BDD por la API (levanta el backend)'),
        ('interfaz', comando_interfaz, 'BDD por la interfaz y E2E (levanta backend y frontend)'),
        ('todo', comando_todo, 'backend, api e interfaz seguidos'),
    ):
        sub = comandos.add_parser(nombre, help=ayuda)
        sub.set_defaults(funcion=funcion)
        if nombre != 'base':
            sub.add_argument('--allure', action='store_true', help=f'guarda resultados en {RESULTADOS_ALLURE.relative_to(RAIZ)}')
            sub.add_argument('--limpiar-allure', action='store_true', help='borra los resultados anteriores (todo lo hace siempre)')
        if nombre in ('interfaz', 'todo'):
            sub.add_argument('--browser', action='append', choices=NAVEGADORES,
                             help='navegador; se puede repetir (por defecto, chromium)')
    return parser


def main():
    """Punto de entrada: corre el comando elegido y devuelve su código de salida."""
    args = crear_parser().parse_args()
    if getattr(args, 'browser', None) is None and args.comando in ('interfaz', 'todo'):
        args.browser = ['chromium']
    return args.funcion(args)


if __name__ == '__main__':
    sys.exit(main())
