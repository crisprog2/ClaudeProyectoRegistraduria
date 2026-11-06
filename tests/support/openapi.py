"""Lectura de la especificación OpenAPI publicada y validación de respuestas contra ella."""
import copy

from jsonschema import Draft202012Validator

from support.api_client import RUTA_CONSULTA

TIPO_JSON = 'application/json'


def _sin_propiedades_extra(nodo):
    """
    Copia el esquema marcando cada objeto con additionalProperties: false.

    OpenAPI permite por defecto campos no documentados. Sin esto, un dato que
    la API empezara a exponer sin documentarlo pasaría la validación.
    """
    copia = copy.deepcopy(nodo)
    pendientes = [copia]
    while pendientes:
        actual = pendientes.pop()
        if isinstance(actual, dict):
            if 'properties' in actual:
                actual['additionalProperties'] = False
            pendientes.extend(actual.values())
        elif isinstance(actual, list):
            pendientes.extend(actual)
    return copia


class EspecificacionOpenApi:
    """Lo que la especificación dice sobre POST /api/consulta/."""

    def __init__(self, contenido):
        """Recibe la especificación ya convertida a diccionario."""
        self.contenido = contenido
        self.operacion = contenido['paths'][RUTA_CONSULTA]['post']
        self._componentes = _sin_propiedades_extra(contenido['components'])

    @property
    def codigos_http(self):
        """Códigos HTTP documentados en la operación."""
        return {int(codigo) for codigo in self.operacion['responses']}

    def propiedades(self, componente):
        """Nombres de los campos de un componente, p. ej. 'Ciudadano'."""
        return set(self.contenido['components']['schemas'][componente]['properties'])

    def ejemplos_solicitud(self):
        """Ejemplos documentados del cuerpo de la petición."""
        return list(self.operacion['requestBody']['content'][TIPO_JSON]['examples'].values())

    def ejemplos_respuesta(self, http):
        """Cuerpos de ejemplo documentados para un código HTTP."""
        contenido = self.operacion['responses'][str(http)]['content'][TIPO_JSON]
        return [ejemplo['value'] for ejemplo in contenido['examples'].values()]

    def errores_de_validacion(self, http, cuerpo):
        """Lista de diferencias entre un cuerpo de respuesta y su esquema documentado; vacía si coincide."""
        esquema = self.operacion['responses'][str(http)]['content'][TIPO_JSON]['schema']
        validador = Draft202012Validator({**esquema, 'components': self._componentes})
        return [error.message for error in validador.iter_errors(cuerpo)]
