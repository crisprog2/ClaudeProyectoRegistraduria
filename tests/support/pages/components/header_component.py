"""Componente de página: marca ficticia y navegación principal."""


class HeaderComponent:
    """Marca ConsultaVoto y enlaces de la navegación principal."""

    def __init__(self, page):
        """Ubica la marca y la navegación por su rol."""
        self.marca = page.get_by_role('banner').get_by_role('link', name='CONSULTAVOTO')
        self.navegacion = page.get_by_role('navigation', name='Principal')
        self.enlace_consulta = self.navegacion.get_by_role('link', name='Consulta electoral')
