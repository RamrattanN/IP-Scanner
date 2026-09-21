from fastapi.testclient import TestClient

from network_scanner.app import app


def test_health_ping():
    response = TestClient(app).get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
