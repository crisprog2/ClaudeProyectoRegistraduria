"""Page Object de Swagger UI (/api/docs/), servida por el backend."""
import json
import re

from support.api_client import RUTA_DOCUMENTACION


class DocumentacionApiPage:
    """
    Pantalla de Swagger UI con la operación POST /api/consulta/.

    La interfaz es de un tercero con versión fijada; se localiza por rol y
    nombre accesible, igual que el resto de los Page Objects.
    """

    def __init__(self, page, url_backend):
        """Guarda la página de Playwright y la URL base del backend."""
        self.page = page
        self.url = url_backend + RUTA_DOCUMENTACION
        self.titulo = page.get_by_role('heading', name=re.compile('ConsultaVoto API'))
        self.operacion = page.get_by_role('button', name=re.compile(r'POST.*consulta'))

    def abrir(self):
        """Abre Swagger UI y espera a que se muestre la especificación."""
        self.page.goto(self.url)
        self.titulo.wait_for()

    def ejecutar_ejemplo_por_defecto(self):
        """Despliega la operación, activa 'Try it out', ejecuta y devuelve (http, cuerpo) de la API."""
        self.operacion.click()
        self.page.get_by_role('button', name='Try it out').click()
        with self.page.expect_response(lambda respuesta: respuesta.request.method == 'POST') as info:
            self.page.get_by_role('button', name='Execute').click()
        return info.value.status, json.loads(info.value.text())
