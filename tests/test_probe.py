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

    async def tcp_open(_ip, port, timeout=0.45):
        return port in {80, 445}

    async def reverse_dns(_ip):
        return "printer.local"

    monkeypatch.setattr(probe, "_ping", reachable)
    monkeypatch.setattr(probe, "_tcp_open", tcp_open)
    monkeypatch.setattr(probe, "_reverse_dns", reverse_dns)

    result = asyncio.run(probe.probe_host("192.0.2.10"))

    assert result["reachable"] is True
    assert result["flags"]["P"] is True
    assert result["flags"]["W"] is True
    assert result["name"] == "printer.local"
    assert result["open_ports"] == [80, 445]
    assert result["services"] == ["HTTP", "SMB"]
    assert result["evidence"] == ["ICMP", "TCP"]
