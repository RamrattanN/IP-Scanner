from __future__ import annotations

import asyncio
import ipaddress
import time
from dataclasses import dataclass
from typing import Any, Dict, List

from .neighbors import get_neighbor_table
from .probe import probe_host


@dataclass
class ScannerConfig:
    concurrency: int = 64


class Scanner:
    def __init__(self, config: ScannerConfig):
        self.config = config

    async def run(self, scan_record: Dict[str, Any]) -> Dict[str, Any]:
        start = ipaddress.IPv4Address(scan_record["range"]["start"])
        end = ipaddress.IPv4Address(scan_record["range"]["end"])
        gateway_ip = (scan_record.get("adapter") or {}).get("gateway")
        ips = [str(ipaddress.IPv4Address(value)) for value in range(int(start), int(end) + 1)]
        requested = set(ips)

        t0 = time.perf_counter()
        sem = asyncio.Semaphore(self.config.concurrency)
        results_by_ip: dict[str, Dict[str, Any]] = {}
        attempted = 0
        probe_errors = 0

        async def worker(ip: str) -> None:
            nonlocal attempted, probe_errors
            async with sem:
                attempted += 1
                try:
                    host = await probe_host(ip)
                except Exception:
                    probe_errors += 1
                    return
                if host.get("reachable"):
                    results_by_ip[ip] = host

        await asyncio.gather(*(worker(ip) for ip in ips))

        # TCP attempts populate the local ARP cache even when a device rejects
        # the connection or blocks ICMP.  Merge those layer-2 observations.
        neighbor_only = 0
        for ip, mac in get_neighbor_table().items():
            if ip not in requested:
                continue
            host = results_by_ip.get(ip)
            if host is None:
                neighbor_only += 1
                host = {
                    "ip": ip,
                    "name": None,
                    "mac": mac,
                    "reachable": True,
                    "evidence": ["ARP"],
                    "open_ports": [],
                    "services": [],
                    "flags": {"G": False, "W": False, "U": False, "B": False, "P": False, "6": False},
                    "notes": {},
                }
                results_by_ip[ip] = host
            else:
                host["mac"] = mac
                if "ARP" not in host["evidence"]:
                    host["evidence"].append("ARP")

        results: List[Dict[str, Any]] = list(results_by_ip.values())
        for host in results:
            if gateway_ip and host["ip"] == gateway_ip:
                host["flags"]["G"] = True

        results.sort(key=lambda host: ipaddress.IPv4Address(host["ip"]))
        duration_ms = int((time.perf_counter() - t0) * 1000)

        scan_record = dict(scan_record)
        scan_record["hosts"] = results
        scan_record["stats"] = {
            "addresses_requested": len(ips),
            "addresses_attempted": attempted,
            "probe_errors": probe_errors,
            "hosts_up": len(results),
            "ping_replies": sum(1 for host in results if host["flags"].get("P")),
            "neighbor_only": neighbor_only,
            "website": sum(1 for host in results if host["flags"].get("W")),
            "upnp": sum(1 for host in results if host["flags"].get("U")),
            "bonjour": sum(1 for host in results if host["flags"].get("B")),
            "ipv6": sum(1 for host in results if host["flags"].get("6")),
            "duration_ms": duration_ms,
            "cancelled": False,
        }
        return scan_record
