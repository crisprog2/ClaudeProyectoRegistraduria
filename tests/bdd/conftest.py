"""
Fixtures del nivel BDD.

Los mismos features se ejecutan por dos canales, cada uno con sus steps:
step_defs/api (HTTP, marker api) y step_defs/interfaz (Playwright, marker e2e).
Cada carpeta tiene su conftest.py porque los textos de los steps son iguales y
sus implementaciones no deben mezclarse.
"""
