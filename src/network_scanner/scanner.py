from __future__ import annotations

import asyncio
import ipaddress
import logging
import time
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List

from .discovery import (
    discover_mdns,
    discover_netbios_name,
    discover_upnp,
    format_mac_address,
    is_valid_unicast_mac,
    subnet_reserved_addresses,
)
from .neighbors import get_neighbor_table
from .probe import probe_host
from .vendors import lookup_mac_vendor
from .device_types import classify_device_type
from .device_intelligence import infer_identity_from_direct_vendor


FLAGS = {"G": False, "W": False, "U": False, "B": False, "P": False, "6": False}
NAME_PRIORITY = {"UPnP": 0, "mDNS": 1, "NetBIOS": 2, "Reverse DNS": 3, "Web title": 4}
PROXY_MAC_THRESHOLD = 4
logger = logging.getLogger(__name__)


@dataclass
class ScannerConfig:
    # Finder-launched macOS applications commonly have a 256 descriptor soft
    # limit.  Bound host and TCP work independently so 14 ports per host cannot
    # exhaust that limit.
    concurrency: int = 32
    tcp_concurrency: int = 96
    passes: int = 2
    retry_delay_seconds: float = 0.2
    neighbor_settle_seconds: float = 0.35
    neighbor_snapshot_count: int = 3
    neighbor_snapshot_interval_seconds: float = 0.15


def _empty_host(ip: str) -> Dict[str, Any]:
    return {
        "ip": ip,
        "name": None,
        "names": [],
        "manufacturer": None,
        "model": None,
        "mac": None,
        "reachable": True,
        "evidence": [],
        "open_ports": [],
        "services": [],
        "flags": dict(FLAGS),
        "notes": {},
    }


def _safe_passive_discovery(discover) -> dict[str, dict[str, Any]]:
    try:
        return discover()
    except Exception:
        logger.exception("Passive discovery failed in %s", getattr(discover, "__name__", discover))
        return {}


def _normalise_host(host: Dict[str, Any]) -> Dict[str, Any]:
    normalised = _empty_host(host["ip"])
    normalised.update(host)
    normalised["names"] = list(host.get("names") or [])
    if host.get("name") and not normalised["names"]:
        normalised["names"].append({"source": "Reverse DNS", "value": host["name"]})
    normalised["evidence"] = list(host.get("evidence") or [])
    normalised["open_ports"] = list(host.get("open_ports") or [])
    normalised["services"] = list(host.get("services") or [])
    normalised["flags"] = {**FLAGS, **(host.get("flags") or {})}
    normalised["notes"] = dict(host.get("notes") or {})
    return normalised


def _add_name(host: Dict[str, Any], source: str, value: str | None) -> None:
    value = (value or "").strip().rstrip(".")
    if not value:
        return
    candidate = {"source": source, "value": value}
    if candidate not in host["names"]:
        host["names"].append(candidate)


def _merge_discovery(host: Dict[str, Any], details: Dict[str, Any], source: str) -> None:
    _add_name(host, source, details.get("name"))
    if details.get("manufacturer"):
        host["manufacturer"] = details["manufacturer"]
    if details.get("model"):
        host["model"] = details["model"]
    if source not in host["evidence"]:
        host["evidence"].append(source)
    for service in details.get("services") or []:
        if service not in host["services"]:
            host["services"].append(service)
    host["notes"].update(details.get("properties") or {})
    if source == "mDNS":
        host["flags"]["B"] = True
    elif source == "UPnP":
        host["flags"]["U"] = True


def _finalise_identity(host: Dict[str, Any]) -> None:
    web_title = host["notes"].get("web_title")
    if web_title and web_title.casefold() not in {"home", "login", "index"}:
        _add_name(host, "Web title", web_title)
    if host["names"]:
        host["names"].sort(key=lambda item: (NAME_PRIORITY.get(item["source"], 99), item["value"]))
        host["name"] = host["names"][0]["value"]

    active_evidence = {item for item in host["evidence"] if item != "ARP"}
    if len(active_evidence) >= 2 or active_evidence.intersection({"mDNS", "UPnP", "NetBIOS"}):
        host["confidence"] = "High"
    elif active_evidence:
        host["confidence"] = "Medium"
    else:
        host["confidence"] = "Observed"


class Scanner:
    def __init__(self, config: ScannerConfig):
        self.config = config

    async def run(self, scan_record: Dict[str, Any]) -> Dict[str, Any]:
        start = ipaddress.IPv4Address(scan_record["range"]["start"])
        end = ipaddress.IPv4Address(scan_record["range"]["end"])
        gateway_ip = (scan_record.get("adapter") or {}).get("gateway")
        ips = [str(ipaddress.IPv4Address(value)) for value in range(int(start), int(end) + 1)]
        requested = set(ips)
        reserved = subnet_reserved_addresses(scan_record.get("cidr"))

        t0 = time.perf_counter()
        sem = asyncio.Semaphore(self.config.concurrency)
        tcp_sem = asyncio.Semaphore(self.config.tcp_concurrency)
        results_by_ip: dict[str, Dict[str, Any]] = {}
        attempted_ips: set[str] = set()
        probe_attempts = 0
        probe_errors_by_ip: dict[str, str] = {}
        neighbor_snapshots: list[dict[str, str]] = []
        initial_neighbors = get_neighbor_table()
        pass_diagnostics: list[dict[str, int]] = []

        mdns_task = asyncio.create_task(
            asyncio.to_thread(_safe_passive_discovery, discover_mdns)
        )
        upnp_task = asyncio.create_task(
            asyncio.to_thread(_safe_passive_discovery, discover_upnp)
        )

        async def worker(ip: str) -> None:
            nonlocal probe_attempts
            async with sem:
                attempted_ips.add(ip)
                probe_attempts += 1
                try:
                    host = await probe_host(ip, tcp_semaphore=tcp_sem)
                    probe_errors_by_ip.pop(ip, None)
                except Exception as exc:
                    probe_errors_by_ip[ip] = type(exc).__name__
                    logger.warning(
                        "Active probe failed for %s: %s: %s",
                        ip,
                        type(exc).__name__,
                        exc,
                    )
                    return
                if host.get("reachable") and ip not in reserved:
                    results_by_ip[ip] = _normalise_host(host)

        for pass_number in range(max(1, self.config.passes)):
            candidates = ips if pass_number == 0 else [
                ip for ip in ips if ip not in results_by_ip and ip not in reserved
            ]
            if not candidates:
                break
            if pass_number:
                await asyncio.sleep(self.config.retry_delay_seconds)
            responses_before = set(results_by_ip)
            await asyncio.gather(*(worker(ip) for ip in candidates))
            if self.config.neighbor_settle_seconds > 0:
                await asyncio.sleep(self.config.neighbor_settle_seconds)
            pass_snapshots: list[dict[str, str]] = []
            for snapshot_number in range(max(1, self.config.neighbor_snapshot_count)):
                if snapshot_number and self.config.neighbor_snapshot_interval_seconds > 0:
                    await asyncio.sleep(self.config.neighbor_snapshot_interval_seconds)
                snapshot = get_neighbor_table()
                pass_snapshots.append(snapshot)
                neighbor_snapshots.append(snapshot)
            requested_neighbors = {
                ip
                for snapshot in pass_snapshots
                for ip in snapshot
                if ip in requested and ip not in reserved
            }
            pass_diagnostics.append(
                {
                    "pass": pass_number + 1,
                    "addresses_probed": len(candidates),
                    "new_active_responses": len(set(results_by_ip) - responses_before),
                    "active_responses_total": len(results_by_ip),
                    "requested_neighbors_observed": len(requested_neighbors),
                    "neighbor_snapshots": len(pass_snapshots),
                    "probe_errors_outstanding": len(probe_errors_by_ip),
                }
            )

        mdns_devices, upnp_devices = await asyncio.gather(mdns_task, upnp_task)

        merged_neighbors: dict[str, str] = {}
        for snapshot in neighbor_snapshots:
            merged_neighbors.update(snapshot)
        neighbor_table = {
            ip: format_mac_address(mac)
            for ip, mac in merged_neighbors.items()
            if ip in requested and ip not in reserved and is_valid_unicast_mac(mac)
        }
        mac_counts = Counter(neighbor_table.values())
        proxy_arp_observed = 0
        for ip, mac in neighbor_table.items():
            shared_mac = mac_counts[mac] >= PROXY_MAC_THRESHOLD
            host = results_by_ip.get(ip)
            if shared_mac:
                if host is None:
                    host = _empty_host(ip)
                    host["evidence"].append("ARP")
                    results_by_ip[ip] = host
                proxy_arp_observed += 1
                host["notes"]["shared_proxy_mac"] = mac
                shared_vendor = lookup_mac_vendor(mac)
                if shared_vendor:
                    host["notes"]["shared_proxy_vendor"] = shared_vendor
                continue
            if host is None:
                host = _empty_host(ip)
                results_by_ip[ip] = host
            host["mac"] = mac
            if "ARP" not in host["evidence"]:
                host["evidence"].append("ARP")

        for source, devices in (("mDNS", mdns_devices), ("UPnP", upnp_devices)):
            for ip, details in devices.items():
                if ip not in requested or ip in reserved:
                    continue
                host = results_by_ip.setdefault(ip, _empty_host(ip))
                _merge_discovery(host, details, source)

        # NetBIOS is queried only for observed addresses, not the whole range.
        netbios_sem = asyncio.Semaphore(24)

        async def enrich_netbios(host: Dict[str, Any]) -> None:
            if host["names"]:
                return
            async with netbios_sem:
                try:
                    name = await discover_netbios_name(host["ip"])
                except Exception:
                    name = None
            if name:
                _add_name(host, "NetBIOS", name)
                if "NetBIOS" not in host["evidence"]:
                    host["evidence"].append("NetBIOS")

        await asyncio.gather(*(enrich_netbios(host) for host in results_by_ip.values()))

        results: List[Dict[str, Any]] = list(results_by_ip.values())
        for host in results:
            if gateway_ip and host["ip"] == gateway_ip:
                host["flags"]["G"] = True
            if host.get("mac"):
                host["mac"] = format_mac_address(host["mac"])
            if host.get("mac"):
                host["mac_vendor"] = lookup_mac_vendor(host["mac"])
            if not host.get("manufacturer") and host.get("mac_vendor"):
                host["manufacturer"] = host["mac_vendor"]
                if host.get("manufacturer"):
                    host["notes"]["manufacturer_source"] = "IEEE OUI"
            _finalise_identity(host)
            infer_identity_from_direct_vendor(host)
            host["device_type"] = classify_device_type(host)

        results.sort(key=lambda host: ipaddress.IPv4Address(host["ip"]))
        duration_ms = int((time.perf_counter() - t0) * 1000)
        direct_results = [host for host in results if not host["notes"].get("shared_proxy_mac")]
        shared_proxy_results = [host for host in results if host["notes"].get("shared_proxy_mac")]
        confirmed = sum(
            1 for host in direct_results if host["confidence"] in {"High", "Medium"}
        )
        observed = sum(1 for host in direct_results if host["confidence"] == "Observed")
        initial_requested_neighbors = sum(
            1 for ip in initial_neighbors if ip in requested and ip not in reserved
        )

        scan_record = dict(scan_record)
        scan_record["hosts"] = results
        scan_record["stats"] = {
            "addresses_requested": len(ips),
            "addresses_attempted": len(attempted_ips),
            "active_probe_attempts": probe_attempts,
            "probe_errors": len(probe_errors_by_ip),
            "probe_error_types": dict(Counter(probe_errors_by_ip.values())),
            "hosts_up": len(direct_results),
            "observations_total": len(results),
            "confirmed_devices": confirmed,
            "observed_devices": observed,
            "ping_replies": sum(1 for host in results if host["flags"].get("P")),
            "neighbor_only": observed,
            "shared_proxy_observations": len(shared_proxy_results),
            "proxy_arp_observed": proxy_arp_observed,
            # Retained for compatibility with existing history readers.
            "proxy_arp_ignored": 0,
            "reserved_ignored": len(requested.intersection(reserved)),
            "website": sum(1 for host in results if host["flags"].get("W")),
            "upnp": sum(1 for host in results if host["flags"].get("U")),
            "bonjour": sum(1 for host in results if host["flags"].get("B")),
            "ipv6": sum(1 for host in results if host["flags"].get("6")),
            "duration_ms": duration_ms,
            "cancelled": False,
        }
        scan_record["diagnostics"] = {
            "initial_requested_neighbors": initial_requested_neighbors,
            "passes": pass_diagnostics,
            "neighbor_snapshots": len(neighbor_snapshots),
            "merged_requested_neighbors": len(neighbor_table),
            "mdns_devices": len(mdns_devices),
            "upnp_devices": len(upnp_devices),
        }
        logger.info(
            "Scan diagnostics: direct=%s shared_proxy=%s observations=%s passes=%s",
            len(direct_results),
            len(shared_proxy_results),
            len(results),
            pass_diagnostics,
        )
        return scan_record
