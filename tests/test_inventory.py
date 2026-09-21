from network_scanner.inventory import (
    reconcile_inventory,
    seed_inventory_from_history,
    update_user_label,
)


def scan(timestamp, scan_id, hosts, cidr="192.0.2.0/24"):
    return {
        "id": scan_id,
        "timestamp_utc": timestamp,
        "cidr": cidr,
        "adapter": {"name": "test"},
        "hosts": hosts,
    }


def host(ip, mac=None, name=None, confidence="Medium"):
    return {
        "ip": ip,
        "mac": mac,
        "name": name,
        "names": [{"source": "mDNS", "value": name}] if name else [],
        "manufacturer": None,
        "model": None,
        "confidence": confidence,
        "evidence": ["ICMP"],
        "services": [],
        "flags": {"G": False},
    }


def test_inventory_reconciles_by_mac_and_preserves_user_label():
    inventory = reconcile_inventory(
        {"version": 1, "devices": []},
        scan("2026-09-21T01:00:00Z", "scan-1", [host("192.0.2.10", "00:11:22:33:44:55", "Printer")]),
    )
    device_id = inventory["devices"][0]["id"]
    update_user_label(inventory, device_id, "Office printer")

    inventory = reconcile_inventory(
        inventory,
        scan("2026-09-21T02:00:00Z", "scan-2", [host("192.0.2.12", "00-11-22-33-44-55", "Printer 500")]),
    )

    assert len(inventory["devices"]) == 1
    device = inventory["devices"][0]
    assert device["id"] == device_id
    assert device["user_label"] == "Office printer"
    assert device["last_ip"] == "192.0.2.12"
    assert device["mac"] == "00:11:22:33:44:55"
    assert device["observation_count"] == 2
    assert device["known_names"] == ["Printer", "Printer 500"]


def test_inventory_upgrades_network_ip_identity_when_mac_appears():
    inventory = reconcile_inventory(
        {"version": 1, "devices": []},
        scan("2026-09-21T01:00:00Z", "scan-1", [host("192.0.2.20", name="TV")]),
    )
    device_id = inventory["devices"][0]["id"]

    inventory = reconcile_inventory(
        inventory,
        scan("2026-09-21T02:00:00Z", "scan-2", [host("192.0.2.20", "10:20:30:40:50:60", "TV")]),
    )

    assert len(inventory["devices"]) == 1
    assert inventory["devices"][0]["id"] == device_id
    assert inventory["devices"][0]["identity_basis"] == "mac"


def test_inventory_does_not_collapse_different_macs_at_reused_ip():
    inventory = reconcile_inventory(
        {"version": 1, "devices": []},
        scan("2026-09-21T01:00:00Z", "scan-1", [host("192.0.2.30", "00:11:22:33:44:55")]),
    )
    inventory = reconcile_inventory(
        inventory,
        scan("2026-09-21T02:00:00Z", "scan-2", [host("192.0.2.30", "00:11:22:33:44:66")]),
    )

    assert len(inventory["devices"]) == 2
    assert {device["mac"] for device in inventory["devices"]} == {
        "00:11:22:33:44:55",
        "00:11:22:33:44:66",
    }


def test_blank_user_label_removes_label():
    inventory = reconcile_inventory(
        {"version": 1, "devices": []},
        scan("2026-09-21T01:00:00Z", "scan-1", [host("192.0.2.40")]),
    )
    device = inventory["devices"][0]
    update_user_label(inventory, device["id"], "Desk")
    assert device["user_label"] == "Desk"

    update_user_label(inventory, device["id"], "  ")
    assert device["user_label"] is None


def test_empty_inventory_is_seeded_from_latest_scan_only():
    older = scan(
        "2026-09-21T01:00:00Z", "scan-1", [host("192.0.2.10", name="Old")]
    )
    latest = scan(
        "2026-09-21T02:00:00Z", "scan-2", [host("192.0.2.20", name="Latest")]
    )

    inventory = seed_inventory_from_history(
        {"version": 1, "devices": []}, {"version": 1, "scans": [older, latest]}
    )

    assert len(inventory["devices"]) == 1
    assert inventory["devices"][0]["name"] == "Latest"
