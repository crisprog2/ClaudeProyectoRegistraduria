"""
Cliente HTTP de la sesión (/api/auth/) para las pruebas black-box.

A diferencia de ConsultaApiClient, que se comparte en toda la corrida, cada prueba
usa un cliente nuevo: guarda la cookie del token de refresco como lo haría un
navegador, y esa cookie no debe pasar de una prueba a otra.
"""
import requests

from support import config
from support.data_loader import cargar

SESION = cargar('sesion')
RUTAS = SESION['rutas']
COOKIE = SESION['cookie']
CABECERA_APP = {SESION['cabecera_app']['nombre']: SESION['cabecera_app']['valor']}


class SesionApiClient:
    """Inicia, renueva y cierra la sesión sobre una requests.Session propia, con sus cookies."""

    def __init__(self, base_url=config.API_BASE_URL, timeout=config.TIMEOUT_SEGUNDOS):
        """Crea la sesión HTTP contra base_url (por defecto, API_BASE_URL del .env)."""
        self.base_url = base_url
        self.timeout = timeout
        self.sesion = requests.Session()
        # Para adjuntar la petición y la respuesta al reporte de Allure cuando una prueba falla.
        self.ultima_respuesta = None

    def _pedir(self, metodo, nombre_ruta, **kwargs):
        """Petición a una ruta de tests/data/sesion.json; guarda la respuesta."""
        url = self.base_url + RUTAS[nombre_ruta]
        self.ultima_respuesta = self.sesion.request(metodo, url, timeout=self.timeout, **kwargs)
        return self.ultima_respuesta

    def ingresar(self, usuario, contrasena):
        """Inicia sesión con usuario y contraseña."""
        return self._pedir('POST', 'ingresar', json={'usuario': usuario, 'contrasena': contrasena})

    def ingresar_como(self, caso_usuario):
        """Inicia sesión con un usuario de tests/data/usuarios.json y su contraseña del .env."""
        return self.ingresar(caso_usuario['usuario'], config.contrasena_demo(caso_usuario['variable_contrasena']))

    def enviar_ingreso(self, cuerpo):
        """POST a ingresar con cualquier cuerpo JSON, para los casos inválidos."""
        return self._pedir('POST', 'ingresar', json=cuerpo)

    def refrescar(self, con_cabecera=True):
        """Renueva la sesión con la cookie guardada (y la cabecera propia de la aplicación)."""
        return self._pedir('POST', 'refrescar', headers=CABECERA_APP if con_cabecera else {})

    def salir(self, con_cabecera=True):
        """Cierra la sesión."""
        return self._pedir('POST', 'salir', headers=CABECERA_APP if con_cabecera else {})

    def ver_sesion(self, acceso=None, cabecera_autorizacion=None):
        """GET a sesion con 'Authorization: Bearer <acceso>', o con la cabecera indicada tal cual."""
        cabecera = cabecera_autorizacion or (f'Bearer {acceso}' if acceso else None)
        return self._pedir('GET', 'sesion', headers={'Authorization': cabecera} if cabecera else {})

    def pedir(self, metodo, nombre_ruta, **kwargs):
        """Petición libre a una ruta de la sesión (p. ej. un método no permitido)."""
        return self._pedir(metodo, nombre_ruta, **kwargs)

    @property
    def cookie_refresco(self):
        """Valor de la cookie del token de refresco que tiene guardada el cliente, o None."""
        return self.sesion.cookies.get(COOKIE['nombre'], path=COOKIE['ruta'])

    def poner_cookie_refresco(self, valor):
        """Reemplaza la cookie guardada, p. ej. para reutilizar una ya revocada."""
        self.sesion.cookies.set(COOKIE['nombre'], valor, path=COOKIE['ruta'])

    def cerrar(self):
        """Cierra la sesión HTTP."""
        self.sesion.close()
