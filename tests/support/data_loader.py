"""Carga de los datos de prueba de tests/data (archivos JSON)."""
import json
from pathlib import Path

import pytest

CARPETA_DATOS = Path(__file__).resolve().parent.parent / 'data'


def cargar(nombre):
    """Lee tests/data/<nombre>.json. Devuelve un objeto nuevo en cada llamada (sin estado compartido)."""
    with open(CARPETA_DATOS / f'{nombre}.json', encoding='utf-8') as archivo:
        return json.load(archivo)


def caso(nombre, id_caso):
    """Devuelve el registro con el id indicado de tests/data/<nombre>.json."""
    for registro in cargar(nombre):
        if registro['id'] == id_caso:
            return registro
    raise KeyError(f"No existe el caso '{id_caso}' en tests/data/{nombre}.json")


def como_parametros(nombre):
    """Registros de tests/data/<nombre>.json como pytest.param, con su id y el marker smoke si lo indican."""
    return [
        pytest.param(registro, id=registro['id'], marks=[pytest.mark.smoke] if registro.get('smoke') else [])
        for registro in cargar(nombre)
    ]
