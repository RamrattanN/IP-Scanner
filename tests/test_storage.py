from network_scanner.storage import ensure_history_file, load_history, save_history


def test_history_round_trip(tmp_path):
    ensure_history_file(tmp_path)
    assert load_history(tmp_path) == {"version": 1, "scans": []}

    expected = {"version": 1, "scans": [{"id": "scan-1"}]}
    save_history(tmp_path, expected)

    assert load_history(tmp_path) == expected
    assert not (tmp_path / "history.tmp").exists()
