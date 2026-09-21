import socket
from types import SimpleNamespace

from network_scanner import adapters


def test_parse_macos_default_route(monkeypatch):
    output = """route to: default
gateway: 192.168.1.1
interface: en0
"""
    monkeypatch.setattr(adapters.subprocess, "check_output", lambda *args, **kwargs: output)
    assert adapters._get_macos_gateways() == {"en0": "192.168.1.1"}


def test_detect_active_adapter_uses_platform_gateway(monkeypatch):
    address = SimpleNamespace(family=socket.AF_INET, address="192.168.1.20", netmask="255.255.255.0")
    monkeypatch.setattr(adapters.psutil, "net_if_addrs", lambda: {"en0": [address]})
    monkeypatch.setattr(adapters, "get_default_gateways", lambda: {"en0": "192.168.1.1"})

    assert adapters.detect_active_adapter() == {
        "name": "en0",
        "ipv4": "192.168.1.20",
        "netmask": "255.255.255.0",
        "gateway": "192.168.1.1",
        "ssid": None,
    }
