import asyncio

from network_scanner import scanner


def disable_passive_discovery(monkeypatch):
    monkeypatch.setattr(scanner, "discover_mdns", lambda: {})
    monkeypatch.setattr(scanner, "discover_upnp", lambda: {})

    async def no_netbios(_ip):
        return None

    monkeypatch.setattr(scanner, "discover_netbios_name", no_netbios)
    monkeypatch.setattr(scanner, "lookup_mac_vendor", lambda _mac: None)


def test_scanner_keeps_reachable_hosts_and_marks_gateway(monkeypatch):
    async def fake_probe(ip):
        reachable = ip in {"192.0.2.1", "192.0.2.2"}
        return {
            "ip": ip,
            "name": f"host-{ip}" if reachable else None,
            "mac": None,
            "reachable": reachable,
            "evidence": ["ICMP"] if reachable else [],
            "open_ports": [80] if ip == "192.0.2.2" else [],
            "services": ["HTTP"] if ip == "192.0.2.2" else [],
            "flags": {
                "G": False,
                "W": ip == "192.0.2.2",
                "U": False,
                "B": False,
                "P": reachable,
                "6": False,
            },
            "notes": {},
        }

    monkeypatch.setattr(scanner, "probe_host", fake_probe)
    monkeypatch.setattr(scanner, "get_neighbor_table", lambda: {"192.0.2.3": "AA:BB:CC:DD:EE:FF"})
    disable_passive_discovery(monkeypatch)
    record = {
        "cidr": "192.0.2.0/29",
        "range": {"start": "192.0.2.1", "end": "192.0.2.3"},
        "adapter": {"gateway": "192.0.2.1"},
    }

    result = asyncio.run(scanner.Scanner(scanner.ScannerConfig(concurrency=2)).run(record))

    assert [host["ip"] for host in result["hosts"]] == ["192.0.2.1", "192.0.2.2", "192.0.2.3"]
    assert result["hosts"][0]["flags"]["G"] is True
    assert result["hosts"][0]["device_type"] == "Router"
    assert result["hosts"][2]["evidence"] == ["ARP"]
    assert result["stats"]["addresses_requested"] == 3
    assert result["stats"]["addresses_attempted"] == 3
    assert result["stats"]["hosts_up"] == 3
    assert result["stats"]["ping_replies"] == 2
    assert result["stats"]["neighbor_only"] == 1
    assert result["stats"]["confirmed_devices"] == 2
    assert result["stats"]["observed_devices"] == 1
    assert result["stats"]["website"] == 1


def test_scanner_attempts_custom_range_inclusively(monkeypatch):
    attempted = []

    async def fake_probe(ip):
        attempted.append(ip)
        return {"ip": ip, "reachable": False}

    monkeypatch.setattr(scanner, "probe_host", fake_probe)
    monkeypatch.setattr(scanner, "get_neighbor_table", lambda: {})
    disable_passive_discovery(monkeypatch)
    record = {
        "cidr": "192.168.2.0/24",
        "range": {"start": "192.168.2.1", "end": "192.168.2.255"},
        "adapter": {},
    }

    result = asyncio.run(scanner.Scanner(scanner.ScannerConfig(concurrency=16)).run(record))

    assert len(attempted) == 255
    assert set(attempted) == {f"192.168.2.{last}" for last in range(1, 256)}
    assert result["stats"]["addresses_requested"] == 255
    assert result["stats"]["addresses_attempted"] == 255
    assert result["stats"]["reserved_ignored"] == 1


def test_scanner_enriches_identity_and_filters_proxy_arp(monkeypatch):
    async def fake_probe(ip):
        last = int(ip.rsplit(".", 1)[1])
        active = last in {1, 2, 7}
        evidence = ["ICMP"] if last in {1, 7} else (["TCP"] if last == 2 else [])
        return {
            "ip": ip,
            "reachable": active,
            "evidence": evidence,
            "flags": {"P": last in {1, 7}, "W": False},
        }

    shared_mac = "00:11:22:33:44:55"
    monkeypatch.setattr(scanner, "probe_host", fake_probe)
    monkeypatch.setattr(
        scanner,
        "get_neighbor_table",
        lambda: {f"192.0.2.{last}": shared_mac for last in range(2, 7)},
    )
    monkeypatch.setattr(
        scanner,
        "discover_mdns",
        lambda: {"192.0.2.3": {"name": "Living Room TV", "services": ["AIRPLAY"]}},
    )
    monkeypatch.setattr(
        scanner,
        "discover_upnp",
        lambda: {
            "192.0.2.4": {
                "name": "Office Printer",
                "manufacturer": "ExampleCo",
                "model": "Laser 500",
                "services": ["UPnP"],
            }
        },
    )

    async def netbios(ip):
        return "DESKTOP" if ip == "192.0.2.1" else None

    monkeypatch.setattr(scanner, "discover_netbios_name", netbios)
    record = {
        "cidr": "192.0.2.0/29",
        "range": {"start": "192.0.2.1", "end": "192.0.2.7"},
        "adapter": {"gateway": "192.0.2.1"},
    }

    result = asyncio.run(scanner.Scanner(scanner.ScannerConfig(concurrency=4)).run(record))

    assert [host["ip"] for host in result["hosts"]] == [
        "192.0.2.1", "192.0.2.2", "192.0.2.3", "192.0.2.4"
    ]
    by_ip = {host["ip"]: host for host in result["hosts"]}
    assert by_ip["192.0.2.1"]["name"] == "DESKTOP"
    assert by_ip["192.0.2.3"]["name"] == "Living Room TV"
    assert by_ip["192.0.2.4"]["manufacturer"] == "ExampleCo"
    assert by_ip["192.0.2.2"]["notes"]["shared_proxy_mac"] == shared_mac
    assert by_ip["192.0.2.2"]["mac"] is None
    assert result["stats"]["proxy_arp_ignored"] == 4
    assert result["stats"]["reserved_ignored"] == 1
