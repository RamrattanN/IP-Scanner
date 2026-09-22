from pathlib import Path

from network_scanner import desktop


def test_service_command_uses_module_in_source(monkeypatch, tmp_path):
    monkeypatch.setattr(desktop, "is_frozen", lambda: False)

    command = desktop.service_command(8123, tmp_path)

    assert command[1:3] == ["-m", "network_scanner.desktop"]
    assert command[-5:] == ["--service", "--port", "8123", "--data-dir", str(tmp_path)]


def test_service_command_associates_child_with_controller(monkeypatch, tmp_path):
    monkeypatch.setattr(desktop, "is_frozen", lambda: True)
    monkeypatch.setattr(desktop.sys, "executable", "/Applications/IP Scanner")

    command = desktop.service_command(8123, tmp_path, parent_pid=31415)

    assert command[-2:] == ["--parent-pid", "31415"]


def test_existing_url_requires_ready_service(monkeypatch, tmp_path):
    (tmp_path / "instance.json").write_text(
        '{"url": "http://127.0.0.1:8123", "pid": 42}', encoding="utf-8"
    )
    monkeypatch.setattr(desktop, "service_is_ready", lambda url: url.endswith(":8123"))

    assert desktop.existing_url(tmp_path) == "http://127.0.0.1:8123"


def test_instance_lock_excludes_second_controller(tmp_path):
    first = desktop.InstanceLock(tmp_path / "instance.lock")
    second = desktop.InstanceLock(tmp_path / "instance.lock")

    assert first.acquire() is True
    try:
        assert second.acquire() is False
    finally:
        first.release()
