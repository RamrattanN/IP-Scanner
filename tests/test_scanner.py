import asyncio

from network_scanner import scanner


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
    record = {
        "range": {"start": "192.0.2.1", "end": "192.0.2.3"},
        "adapter": {"gateway": "192.0.2.1"},
    }

    result = asyncio.run(scanner.Scanner(scanner.ScannerConfig(concurrency=2)).run(record))

    assert [host["ip"] for host in result["hosts"]] == ["192.0.2.1", "192.0.2.2", "192.0.2.3"]
    assert result["hosts"][0]["flags"]["G"] is True
    assert result["hosts"][2]["evidence"] == ["ARP"]
    assert result["stats"]["addresses_requested"] == 3
    assert result["stats"]["addresses_attempted"] == 3
    assert result["stats"]["hosts_up"] == 3
    assert result["stats"]["ping_replies"] == 2
    assert result["stats"]["neighbor_only"] == 1
    assert result["stats"]["website"] == 1


def test_scanner_attempts_custom_range_inclusively(monkeypatch):
    attempted = []

    async def fake_probe(ip):
        attempted.append(ip)
        return {"ip": ip, "reachable": False}

    monkeypatch.setattr(scanner, "probe_host", fake_probe)
    monkeypatch.setattr(scanner, "get_neighbor_table", lambda: {})
    record = {
        "range": {"start": "192.168.2.1", "end": "192.168.2.255"},
        "adapter": {},
    }

    result = asyncio.run(scanner.Scanner(scanner.ScannerConfig(concurrency=16)).run(record))

    assert len(attempted) == 255
    assert set(attempted) == {f"192.168.2.{last}" for last in range(1, 256)}
    assert result["stats"]["addresses_requested"] == 255
    assert result["stats"]["addresses_attempted"] == 255
