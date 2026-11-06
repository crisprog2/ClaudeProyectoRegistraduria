"""Componente de página: indicador de pasos Consulta -> Resultado."""


class StepperComponent:
    """Lista de pasos; el paso actual está marcado con aria-current="step"."""

    def __init__(self, page):
        """Ubica la lista por su nombre accesible y el paso actual dentro de ella."""
        self.pasos = page.get_by_role('list', name='Progreso de la consulta')
        self.paso_actual = self.pasos.locator('[aria-current="step"]')
