"""Page Object base: navegación y elementos comunes a todas las pantallas."""
from urllib.parse import urlparse

from support.pages.components.demo_banner_component import DemoBannerComponent
from support.pages.components.header_component import HeaderComponent
from support.pages.components.stepper_component import StepperComponent


class BasePage:
    """
    Elementos del layout común. Las subclases definen RUTA.

    Los elementos se ubican por rol y nombre accesible, como los percibe quien
    usa la aplicación. Las pruebas no usan selectores: solo esta capa los conoce.
    """

    RUTA = '/'

    def __init__(self, page):
        """Crea los localizadores del layout y los componentes."""
        self.page = page
        self.demo_banner = DemoBannerComponent(page)
        self.header = HeaderComponent(page)
        self.stepper = StepperComponent(page)
        self.titulo = page.get_by_role('heading', level=1)
        self.pie = page.get_by_role('contentinfo')
        self.migas = page.get_by_role('navigation', name='Ruta de navegación')
        self.saltar = page.get_by_role('link', name='Saltar al contenido')
        self.principal = page.get_by_role('main')

    def abrir(self, ruta=None):
        """Abre la ruta de la pantalla (u otra indicada) y espera a que aparezca el título."""
        self.page.goto(ruta or self.RUTA)
        self.titulo.wait_for()
        return self

    def ruta_actual(self):
        """Ruta y parámetros de la URL actual, sin el dominio."""
        url = urlparse(self.page.url)
        return f'{url.path}?{url.query}' if url.query else url.path

    def recargar(self):
        """Recarga la página como lo haría la persona con F5."""
        self.page.reload()
        self.titulo.wait_for()

    def texto_visible(self):
        """Todo el texto visible de la página."""
        return self.page.locator('body').inner_text()

    def desborde_horizontal(self):
        """Píxeles que la página se sale a lo ancho (0 si no hay barra de desplazamiento horizontal)."""
        return self.page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
