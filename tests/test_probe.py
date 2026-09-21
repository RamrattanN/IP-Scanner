import asyncio

from network_scanner import probe


def test_ping_command_is_platform_specific():
    assert probe.ping_command("192.0.2.1", 400, "win32") == [
        "ping", "-n", "1", "-w", "400", "192.0.2.1"
    ]
    assert probe.ping_command("192.0.2.1", 400, "darwin") == [
        "ping", "-n", "-c", "1", "-W", "400", "192.0.2.1"
    ]
    assert probe.ping_command("192.0.2.1", 400, "linux") == [
        "ping", "-n", "-c", "1", "-W", "1", "192.0.2.1"
    ]


def test_probe_returns_explicit_reachable_contract(monkeypatch):
    async def reachable(_ip):
        return True

    async def no_website(_url, timeout=0.6):
        return False

    monkeypatch.setattr(probe, "_ping", reachable)
    monkeypatch.setattr(probe, "_http_head", no_website)

    result = asyncio.run(probe.probe_host("192.0.2.10"))

    assert result["reachable"] is True
    assert result["flags"]["P"] is True
    assert result["flags"]["W"] is False
