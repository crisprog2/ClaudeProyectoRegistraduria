"""Cliente HTTP de la API de consulta para las pruebas black-box."""
import requests

from support import config

RUTA_CONSULTA = '/api/consulta/'
RUTA_ESQUEMA = '/api/schema/'
RUTA_DOCUMENTACION = '/api/docs/'


class ConsultaApiClient:
    """
    Cliente del endpoint POST /api/consulta/ sobre una requests.Session.

    consultar() cubre el uso normal; enviar() permite armar peticiones
    arbitrarias (otros métodos, cuerpos crudos, cabeceras) para los casos de error.
    """

    def __init__(self, base_url=config.API_BASE_URL, timeout=config.TIMEOUT_SEGUNDOS):
        """Crea la sesión HTTP contra base_url (por defecto, API_BASE_URL del .env)."""
        self.base_url = base_url
        self.timeout = timeout
        self.sesion = requests.Session()

    @property
    def url_consulta(self):
        """URL absoluta del endpoint de consulta."""
        return self.base_url + RUTA_CONSULTA

    def consultar(self, cedula):
        """Envía {"cedula": cedula} como JSON y devuelve la respuesta."""
        return self.enviar_json({'cedula': cedula})

    def enviar_json(self, cuerpo):
        """Envía por POST cualquier objeto serializable a JSON (p. ej. {} o {"cedula": null})."""
        return self.enviar('POST', json=cuerpo)

    def enviar(self, metodo, **kwargs):
        """Petición libre al endpoint de consulta; kwargs se pasan tal cual a requests."""
        return self.sesion.request(metodo, self.url_consulta, timeout=self.timeout, **kwargs)

    def enviar_solicitud(self, solicitud):
        """Envía un caso de solicitudes_invalidas.json: método, cuerpo crudo y Content-Type opcionales."""
        opciones = {}
        if 'cuerpo_crudo' in solicitud:
            opciones['data'] = solicitud['cuerpo_crudo'].encode('utf-8')
            opciones['headers'] = {'Content-Type': solicitud['content_type']}
        return self.enviar(solicitud['metodo'], **opciones)

    def obtener(self, ruta, **kwargs):
        """GET a cualquier ruta del servidor; admite una ruta relativa o una URL absoluta."""
        url = ruta if ruta.startswith('http') else self.base_url + ruta
        return self.sesion.get(url, timeout=self.timeout, **kwargs)

    def servidor_disponible(self):
        """True si hay un servidor escuchando en base_url (no consume el límite de consultas)."""
        try:
            self.sesion.get(self.base_url + '/', timeout=self.timeout)
        except requests.ConnectionError:
            return False
        return True

    def cerrar(self):
        """Cierra la sesión HTTP."""
        self.sesion.close()
