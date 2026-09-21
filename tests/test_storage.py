from network_scanner.storage import (
    ensure_history_file,
    ensure_inventory_file,
    load_history,
    load_inventory,
    save_history,
    save_inventory,
)


def test_history_round_trip(tmp_path):
    ensure_history_file(tmp_path)
    assert load_history(tmp_path) == {"version": 1, "scans": []}

    expected = {"version": 1, "scans": [{"id": "scan-1"}]}
    save_history(tmp_path, expected)

    assert load_history(tmp_path) == expected
    assert not (tmp_path / "history.tmp").exists()


def test_inventory_round_trip(tmp_path):
    ensure_inventory_file(tmp_path)
    assert load_inventory(tmp_path) == {"version": 1, "devices": []}

    expected = {"version": 1, "devices": [{"id": "device-1"}]}
    save_inventory(tmp_path, expected)

    assert load_inventory(tmp_path) == expected
    assert not (tmp_path / "inventory.tmp").exists()
