"""Page Object de la pantalla de consulta por cédula."""
import re
from urllib.parse import urlparse

from support.pages.base_page import BasePage


class ConsultaPage(BasePage):
    """Formulario de consulta y sus estados de error."""

    RUTA = '/consulta'

    def __init__(self, page):
        """Ubica el campo, el botón y la zona de mensajes."""
        super().__init__(page)
        self.campo = page.get_by_label('Número de cédula de ciudadanía')
        self.boton = page.get_by_role('button', name=re.compile('Consultar|Consultando'))
        self.ayuda = page.get_by_text('Escribe solo números, sin puntos, espacios ni comas.', exact=True)
        self.alerta = page.get_by_role('alert')
        self.panel_promocional = page.get_by_role('complementary', name='Participar empieza por estar bien informado.')
        self.pasos = page.get_by_role('region', name='Una consulta sencilla, paso a paso')

    def escribir(self, valor):
        """Escribe en el campo, reemplazando lo que tenga."""
        self.campo.fill(valor)

    def enviar(self):
        """Pulsa el botón Consultar."""
        self.boton.click()

    def consultar(self, cedula):
        """Escribe la cédula y envía el formulario. No espera el resultado."""
        self.escribir(cedula)
        self.enviar()

    def consultar_hasta_resultado(self, cedula):
        """Abre la pantalla, consulta una cédula existente y espera a que cargue el resultado."""
        self.abrir()
        self.consultar(cedula)
        self.page.wait_for_url(lambda url: urlparse(url).path == '/consulta/resultado')
        self.page.get_by_role('region', name='Persona consultada').wait_for()
