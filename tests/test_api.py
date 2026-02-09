import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from parser_site.api import MAX_INPUT_CHARS, app

client = TestClient(app)


def test_parse_endpoint_success() -> None:
    response = client.post(
        "/parse",
        json={"text": "dev@example.com https://example.com +1 (202) 555-0182"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "emails": ["dev@example.com"],
        "urls": ["https://example.com"],
        "phones": ["+12025550182"],
    }


def test_parse_endpoint_rejects_empty_text() -> None:
    response = client.post("/parse", json={"text": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Input text is empty"


def test_parse_endpoint_rejects_oversized_payload() -> None:
    response = client.post("/parse", json={"text": "a" * (MAX_INPUT_CHARS + 1)})

    assert response.status_code == 413
    assert "exceeds maximum length" in response.json()["detail"]


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
