import asyncio

from network_scanner import scanner


def test_scanner_keeps_reachable_hosts_and_marks_gateway(monkeypatch):
    async def fake_probe(ip):
        reachable = ip in {"192.0.2.1", "192.0.2.2"}
        return {
            "ip": ip,
            "name": f"host-{ip}" if reachable else None,
            "reachable": reachable,
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
    record = {
        "range": {"start": "192.0.2.1", "end": "192.0.2.3"},
        "adapter": {"gateway": "192.0.2.1"},
    }

    result = asyncio.run(scanner.Scanner(scanner.ScannerConfig(concurrency=2)).run(record))

    assert [host["ip"] for host in result["hosts"]] == ["192.0.2.1", "192.0.2.2"]
    assert result["hosts"][0]["flags"]["G"] is True
    assert result["stats"]["hosts_up"] == 2
    assert result["stats"]["website"] == 1
