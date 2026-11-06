"""Componente de página: aviso de sitio de demostración, obligatorio en todas las pantallas."""


class DemoBannerComponent:
    """Franja "Sitio de demostración" bajo el header."""

    def __init__(self, page):
        """Ubica el aviso por su rol y su nombre accesible."""
        self.aviso = page.get_by_role('note', name='Aviso de demostración')
