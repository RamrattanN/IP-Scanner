from fastapi.testclient import TestClient

from network_scanner.app import app
from network_scanner import api
from network_scanner.storage import ensure_history_file, save_history


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


def test_history_enriches_existing_mac_and_device_metadata(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "get_app_data_dir", lambda: tmp_path)
    monkeypatch.setattr(api, "lookup_mac_vendor", lambda _mac: "Example Devices")
    ensure_history_file(tmp_path)
    save_history(
        tmp_path,
        {
            "version": 1,
            "scans": [
                {
                    "id": "scan-1",
                    "hosts": [
                        {
                            "ip": "192.0.2.10",
                            "mac": "0-11-22-33-44-55",
                            "name": "Office Printer",
                            "names": [],
                            "services": ["IPP"],
                            "flags": {},
                        }
                    ],
                }
            ],
        },
    )

    response = TestClient(app).get("/api/history")

    host = response.json()["scans"][0]["hosts"][0]
    assert host["mac"] == "00:11:22:33:44:55"
    assert host["mac_vendor"] == "Example Devices"
    assert host["manufacturer"] == "Example Devices"
    assert host["notes"]["manufacturer_source"] == "IEEE OUI"
    assert host["device_type"] == "Printer"


def test_history_labels_shared_mac_vendor_without_claiming_device_identity(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "get_app_data_dir", lambda: tmp_path)
    monkeypatch.setattr(api, "lookup_mac_vendor", lambda _mac: "Ubiquiti Inc")
    ensure_history_file(tmp_path)
    save_history(
        tmp_path,
        {
            "version": 1,
            "scans": [{
                "id": "scan-1",
                "hosts": [{
                    "ip": "192.168.2.102",
                    "mac": None,
                    "name": None,
                    "names": [],
                    "services": [],
                    "flags": {},
                    "notes": {"shared_proxy_mac": "F0:9F:C2:38:9D:53"},
                }],
            }],
        },
    )

    host = TestClient(app).get("/api/history").json()["scans"][0]["hosts"][0]

    assert host["name"] is None
    assert host.get("manufacturer") is None
    assert host.get("mac_vendor") is None
    assert host["notes"]["shared_proxy_vendor"] == "Ubiquiti Inc"
    assert host["device_type"] == "Other"


def test_history_infers_nintendo_identity_and_game_console_type(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "get_app_data_dir", lambda: tmp_path)
    monkeypatch.setattr(api, "lookup_mac_vendor", lambda _mac: "Nintendo Co.,Ltd")
    ensure_history_file(tmp_path)
    save_history(
        tmp_path,
        {
            "version": 1,
            "scans": [{
                "id": "scan-1",
                "hosts": [{
                    "ip": "192.168.2.114",
                    "mac": "70:48:F7:2C:73:DF",
                    "name": None,
                    "names": [],
                    "services": [],
                    "flags": {},
                    "notes": {},
                }],
            }],
        },
    )

    host = TestClient(app).get("/api/history").json()["scans"][0]["hosts"][0]

    assert host["name"] == "Nintendo"
    assert host["names"] == [{"source": "MAC vendor inference", "value": "Nintendo"}]
    assert host["manufacturer"] == "Nintendo Co.,Ltd"
    assert host["mac_vendor"] == "Nintendo Co.,Ltd"
    assert host["device_type"] == "Game Console"
