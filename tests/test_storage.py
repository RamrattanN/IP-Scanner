from network_scanner.storage import (
    ensure_history_file,
    load_history,
    load_settings,
    save_history,
    save_settings,
)


def test_history_round_trip(tmp_path):
    ensure_history_file(tmp_path)
    assert load_history(tmp_path) == {"version": 1, "scans": []}

    expected = {"version": 1, "scans": [{"id": "scan-1"}]}
    save_history(tmp_path, expected)

    assert load_history(tmp_path) == expected
    assert not (tmp_path / "history.tmp").exists()


def test_settings_default_and_round_trip(tmp_path):
    assert load_settings(tmp_path) == {
        "version": 1,
        "automatic_scans": True,
        "interval_minutes": 60,
    }

    save_settings(
        tmp_path,
        {"version": 1, "automatic_scans": False, "interval_minutes": 180},
    )

    assert load_settings(tmp_path)["automatic_scans"] is False
    assert load_settings(tmp_path)["interval_minutes"] == 180
