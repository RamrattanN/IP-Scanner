from fastapi.testclient import TestClient

from network_scanner.app import app
from network_scanner import api
from network_scanner.storage import ensure_history_file


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


def test_inventory_label_api_updates_local_record(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "get_app_data_dir", lambda: tmp_path)
    api.save_inventory(
        tmp_path,
        {"version": 1, "devices": [{"id": "device-1", "user_label": None}]},
    )

    response = TestClient(app).patch(
        "/api/inventory/device-1", json={"label": "Office printer"}
    )

    assert response.status_code == 200
    assert response.json()["device"]["user_label"] == "Office printer"
    assert api.load_inventory(tmp_path)["devices"][0]["user_label"] == "Office printer"


def test_inventory_label_api_rejects_unknown_device(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "get_app_data_dir", lambda: tmp_path)

    response = TestClient(app).patch(
        "/api/inventory/missing", json={"label": "Unknown"}
    )

    assert response.status_code == 404


def test_clearing_history_preserves_inventory(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "get_app_data_dir", lambda: tmp_path)
    ensure_history_file(tmp_path)
    api.save_inventory(
        tmp_path,
        {"version": 1, "devices": [{"id": "device-1", "user_label": "Router"}]},
    )

    response = TestClient(app).post("/api/clear-history")

    assert response.status_code == 200
    assert api.load_inventory(tmp_path)["devices"][0]["user_label"] == "Router"


def test_completed_scan_updates_inventory(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "get_app_data_dir", lambda: tmp_path)
    monkeypatch.setattr(
        api,
        "detect_active_adapter",
        lambda: {
            "name": "test",
            "ipv4": "192.0.2.10",
            "netmask": "255.255.255.0",
            "gateway": "192.0.2.1",
        },
    )
    ensure_history_file(tmp_path)

    async def fake_run(self, record):
        record["hosts"] = [
            {
                "ip": "192.0.2.10",
                "mac": "00:11:22:33:44:55",
                "name": "Test device",
                "names": [{"source": "mDNS", "value": "Test device"}],
                "confidence": "High",
                "evidence": ["ICMP", "mDNS"],
                "services": [],
                "flags": {"G": False},
            }
        ]
        record["stats"] = {"addresses_requested": 1, "addresses_attempted": 1}
        return record

    monkeypatch.setattr(api.Scanner, "run", fake_run)
    response = TestClient(app).post(
        "/api/start-scan", json={"start_ip": "192.0.2.10", "end_ip": "192.0.2.10"}
    )

    assert response.status_code == 200
    inventory = api.load_inventory(tmp_path)
    assert len(inventory["devices"]) == 1
    assert inventory["devices"][0]["name"] == "Test device"
