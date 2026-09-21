from fastapi.testclient import TestClient

from network_scanner.app import app
from network_scanner import api


def test_health_ping():
    response = TestClient(app).get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_custom_range_rejects_reversed_addresses(monkeypatch):
    monkeypatch.setattr(
        api,
        "detect_active_adapter",
        lambda: {"name": "test", "ipv4": "192.168.2.10", "netmask": "255.255.255.0"},
    )
    response = TestClient(app).post(
        "/api/start-scan",
        json={"start_ip": "192.168.2.255", "end_ip": "192.168.2.1"},
    )

    assert response.status_code == 422
    assert "must not precede" in response.json()["detail"]


def test_custom_range_requires_both_endpoints(monkeypatch):
    monkeypatch.setattr(
        api,
        "detect_active_adapter",
        lambda: {"name": "test", "ipv4": "192.168.2.10", "netmask": "255.255.255.0"},
    )
    response = TestClient(app).post(
        "/api/start-scan", json={"start_ip": "192.168.2.1"}
    )

    assert response.status_code == 422
    assert "both" in response.json()["detail"]
