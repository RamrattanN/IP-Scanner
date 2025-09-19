from __future__ import annotations
import asyncio, time, ipaddress
from dataclasses import dataclass
from typing import Dict, Any, List
from .probe import probe_host

@dataclass
class ScannerConfig:
    concurrency: int = 256

class Scanner:
    def __init__(self, config: ScannerConfig):
        self.config = config

    async def run(self, scan_record: Dict[str, Any]) -> Dict[str, Any]:
        start_ip = scan_record["range"]["start"]
        end_ip = scan_record["range"]["end"]
        gateway_ip = (scan_record.get("adapter") or {}).get("gateway")

        start = ipaddress.IPv4Address(start_ip)
        end = ipaddress.IPv4Address(end_ip)
        ips = [str(ipaddress.IPv4Address(i)) for i in range(int(start), int(end) + 1)]

        t0 = time.perf_counter()
        sem = asyncio.Semaphore(self.config.concurrency)
        results: List[Dict[str, Any]] = []

        async def worker(ip: str):
            async with sem:
                host = await probe_host(ip)
                if host.get("reachable"):
                    if gateway_ip and host["ip"] == gateway_ip:
                        host["flags"]["G"] = True
                    results.append({"ip": host["ip"], "name": host["name"], "flags": host["flags"], "notes": {}})

        await asyncio.gather(*[worker(ip) for ip in ips])

        duration_ms = int((time.perf_counter() - t0) * 1000)
        hosts_up = sum(1 for h in results if h["flags"].get("P"))
        website = sum(1 for h in results if h["flags"].get("W"))
        upnp = sum(1 for h in results if h["flags"].get("U"))
        bonjour = sum(1 for h in results if h["flags"].get("B"))
        ipv6 = sum(1 for h in results if h["flags"].get("6"))

        scan_record = dict(scan_record)
        results.sort(key=lambda h: tuple(int(p) for p in h["ip"].split('.')))
        scan_record["hosts"] = results
        scan_record["stats"] = {
            "hosts_up": hosts_up,
            "website": website,
            "upnp": upnp,
            "bonjour": bonjour,
            "ipv6": ipv6,
            "duration_ms": duration_ms,
            "cancelled": False,
        }
        return scan_record
