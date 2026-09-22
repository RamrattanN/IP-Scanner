import asyncio

from network_scanner import probe


def test_ping_command_is_platform_specific():
    assert probe.ping_command("192.0.2.1", 400, "win32") == [
        "ping", "-n", "1", "-w", "400", "192.0.2.1"
    ]
    assert probe.ping_command("192.0.2.1", 400, "darwin") == [
        "/sbin/ping", "-n", "-c", "1", "-W", "400", "192.0.2.1"
    ]
    assert probe.ping_command("192.0.2.1", 400, "linux") == [
        "ping", "-n", "-c", "1", "-W", "1", "192.0.2.1"
    ]


def test_probe_returns_explicit_reachable_contract(monkeypatch):
    async def reachable(_ip):
        return True

    async def tcp_probe(_ip, port, timeout=0.45):
        return probe.TCP_OPEN if port in {80, 445} else probe.TCP_NO_RESPONSE

    async def reverse_dns(_ip):
        return "printer.local"

    async def web_identity(_ip, _ports):
        return {"web_title": "Office Printer", "http_server": "printer-os"}

    monkeypatch.setattr(probe, "_ping", reachable)
    monkeypatch.setattr(probe, "_tcp_probe", tcp_probe)
    monkeypatch.setattr(probe, "_send_udp_stimulus", lambda _ip: None)
    monkeypatch.setattr(probe, "_reverse_dns", reverse_dns)
    monkeypatch.setattr(probe, "_web_identity", web_identity)

    result = asyncio.run(probe.probe_host("192.0.2.10"))

    assert result["reachable"] is True
    assert result["flags"]["P"] is True
    assert result["flags"]["W"] is True
    assert result["name"] == "printer.local"
    assert result["open_ports"] == [80, 445]
    assert result["services"] == ["HTTP", "SMB"]
    assert result["evidence"] == ["ICMP", "TCP"]
    assert result["names"] == [{"source": "Reverse DNS", "value": "printer.local"}]
    assert result["notes"]["web_title"] == "Office Printer"


def test_tcp_refusal_proves_presence_without_claiming_an_open_port(monkeypatch):
    async def no_ping(_ip):
        return False

    async def refused(_ip, _port, timeout=0.45):
        return probe.TCP_RESPONDED

    async def reverse_dns(_ip):
        return None

    monkeypatch.setattr(probe, "_ping", no_ping)
    monkeypatch.setattr(probe, "_tcp_probe", refused)
    monkeypatch.setattr(probe, "_reverse_dns", reverse_dns)
    monkeypatch.setattr(probe, "_send_udp_stimulus", lambda _ip: None)

    result = asyncio.run(probe.probe_host("192.0.2.20"))

    assert result["reachable"] is True
    assert result["open_ports"] == []
    assert result["services"] == []
    assert result["evidence"] == ["TCP"]


def test_shared_tcp_semaphore_bounds_socket_pressure(monkeypatch):
    active = 0
    maximum = 0

    async def no_ping(_ip):
        return False

    async def measured_probe(_ip, _port, timeout=0.45):
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        await asyncio.sleep(0)
        active -= 1
        return probe.TCP_NO_RESPONSE

    monkeypatch.setattr(probe, "_ping", no_ping)
    monkeypatch.setattr(probe, "_tcp_probe", measured_probe)
    monkeypatch.setattr(probe, "_send_udp_stimulus", lambda _ip: None)

    async def exercise():
        semaphore = asyncio.Semaphore(3)
        await asyncio.gather(
            probe.probe_host("192.0.2.30", tcp_semaphore=semaphore),
            probe.probe_host("192.0.2.31", tcp_semaphore=semaphore),
        )

    asyncio.run(exercise())

    assert maximum == 3
