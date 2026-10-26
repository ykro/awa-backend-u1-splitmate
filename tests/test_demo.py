"""Tests de la demo: pasan en verde desde el starter."""

from fastapi.testclient import TestClient


def test_health_ok_and_create_trip_normalizes_names_and_currency(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok", "service": "splitmate-api"}

    response = client.post(
        "/api/v1/trips",
        json={
            "name": "  Ruta   Maya 2027 ",
            "default_currency": "gtq",
            "participants": [" ana ", "LUIS", "sofi\u0301a"],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ruta Maya 2027"
    assert data["default_currency"] == "GTQ"
    assert data["participants"] == ["Ana", "Luis", "Sofía"]
    assert data["expense_count"] == 0
    assert data["total_spent"] == "0.00"


def test_create_trip_rejects_duplicate_participants_after_normalizing(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/trips",
        json={"name": "Viaje duplicado", "participants": ["Ana", "  ana  "]},
    )

    nfd_duplicate = client.post(
        "/api/v1/trips",
        json={"name": "Viaje con acentos", "participants": ["Sofía", "Sofi\u0301a"]},
    )

    hidden_char = client.post(
        "/api/v1/trips",
        json={"name": "Viaje con nulo", "participants": ["Ana", "An\x00a"]},
    )

    assert response.status_code == 422
    assert nfd_duplicate.status_code == 422
    assert hidden_char.status_code == 422
    body = response.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert body["detail"][0]["loc"] == ["body", "participants"]
    assert set(body["detail"][0]) == {"loc", "msg", "type"}
