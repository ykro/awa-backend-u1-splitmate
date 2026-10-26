"""Tus tests propios (15 puntos de la rúbrica).

Tus tests propios suman si pasan contra la solución de referencia y detectan
mutantes que la suite pública no detecta (errores sembrados en el reto en
el reto). Reescribir un test público no suma.

Escribe al menos 2 tests: detectar 2 o más de esos mutantes da el puntaje
completo, 1 da la mitad.

Reglas: usa los fixtures de tests/conftest.py (client, create_trip,
add_expense), no crees conftest.py en esta carpeta y no uses la red.
"""

import pytest
from fastapi.testclient import TestClient


def test_my_scenario_1(client: TestClient) -> None:
    """Describe aquí qué error del reto atrapa este test y renómbralo."""
    pytest.fail("Escribe tu primer test propio")


def test_my_scenario_2(client: TestClient) -> None:
    """Describe aquí qué error del reto atrapa este test y renómbralo."""
    pytest.fail("Escribe tu segundo test propio")
