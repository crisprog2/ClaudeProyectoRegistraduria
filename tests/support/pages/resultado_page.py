"""Page Object de la pantalla de resultado electoral."""
import re

from support.pages.base_page import BasePage


class ResultadoPage(BasePage):
    """Resumen del ciudadano, avisos, tarjetas de mesa y mapa."""

    RUTA = '/consulta/resultado'

    def __init__(self, page):
        """Ubica cada sección por su rol y su nombre accesible."""
        super().__init__(page)
        self.resumen = page.get_by_role('region', name='Persona consultada')
        self.cedula = self.resumen.get_by_text('Cédula de ciudadanía ·')
        self.edad = self.resumen.get_by_text('Edad ·')
        self.badge_ficticio = self.resumen.get_by_text('DATOS FICTICIOS', exact=True)
        self.otra_consulta = page.get_by_role('link', name='Realizar otra consulta')

        self.aviso_votante = page.get_by_role('region', name='Eres votante y no tienes designación como jurado')
        self.aviso_jurado = page.get_by_role('region', name=re.compile('^Tienes una designación como jurado'))
        self.tarjeta_votacion = page.get_by_role('region', name='Tu lugar para votar')
        self.tarjeta_jurado = page.get_by_role('region', name='Tu asignación como jurado')
        self.mapa = page.get_by_role('region', name='Ubica tu puesto')
        self.plano = self.mapa.get_by_role('img', name=re.compile('^Plano ilustrativo'))
        self.consejo = page.get_by_role('complementary', name='Antes de ir a votar')
        # Todas las notas: el consejo del votante y las responsabilidades del jurado.
        self.notas = page.get_by_role('complementary')
        self.aclaracion = page.get_by_text('Esta consulta es una demostración visual.')

    @staticmethod
    def valor_de(tarjeta, etiqueta):
        """Localizador del valor de un dato de la tarjeta, por su etiqueta exacta ('Ciudad', 'Dirección'...)."""
        return tarjeta.locator(f'dt:text-is("{etiqueta}") + dd')

    @staticmethod
    def numero_de_mesa(tarjeta):
        """Número de mesa destacado en la tarjeta ('018'), sin importar la etiqueta que lo acompañe."""
        tarjeta.wait_for()
        return re.search(r'^(\d{3})\b', tarjeta.inner_text(), re.MULTILINE).group(1)
