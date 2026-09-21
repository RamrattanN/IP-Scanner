from __future__ import annotations

import uuid
from typing import Any

from .discovery import is_valid_unicast_mac


def _normalise_mac(value: str | None) -> str | None:
    if not value:
        return None
    normalised = value.replace("-", ":").upper()
    return normalised if is_valid_unicast_mac(normalised) else None


def _network_key(scan: dict[str, Any]) -> str:
    adapter = scan.get("adapter") or {}
    return scan.get("cidr") or adapter.get("name") or "unknown-network"


def _meaningful_names(host: dict[str, Any]) -> set[str]:
    values = {
        item.get("value", "").strip().casefold()
        for item in host.get("names") or []
        if item.get("value")
    }
    if host.get("name"):
        values.add(host["name"].strip().casefold())
    return {value for value in values if value}


def _find_device(
    devices: list[dict[str, Any]], host: dict[str, Any], network_key: str
) -> dict[str, Any] | None:
    mac = _normalise_mac(host.get("mac"))
    if mac:
        for device in devices:
            if _normalise_mac(device.get("mac")) == mac:
                return device

        # Upgrade an IP-based identity when this is the first reliable MAC
        # observed for the same address on the same network.
        candidates = [
            device
            for device in devices
            if device.get("identity_basis") == "network_ip"
            and device.get("network_key") == network_key
            and device.get("last_ip") == host.get("ip")
            and not device.get("mac")
        ]
        return candidates[0] if len(candidates) == 1 else None

    candidates = [
        device
        for device in devices
        if device.get("network_key") == network_key
        and device.get("last_ip") == host.get("ip")
    ]
    if len(candidates) != 1:
        return None
    candidate = candidates[0]
    if candidate.get("identity_basis") == "network_ip":
        return candidate

    known_names = {value.casefold() for value in candidate.get("known_names") or []}
    return candidate if known_names.intersection(_meaningful_names(host)) else None


def _new_device(host: dict[str, Any], scan: dict[str, Any], network_key: str) -> dict[str, Any]:
    timestamp = scan["timestamp_utc"]
    mac = _normalise_mac(host.get("mac"))
    return {
        "id": str(uuid.uuid4()),
        "user_label": None,
        "identity_basis": "mac" if mac else "network_ip",
        "first_seen_utc": timestamp,
        "last_seen_utc": timestamp,
        "observation_count": 0,
        "network_key": network_key,
        "last_scan_id": scan.get("id"),
        "last_ip": host.get("ip"),
        "mac": mac,
        "name": None,
        "known_names": [],
        "manufacturer": None,
        "model": None,
        "confidence": None,
        "evidence": [],
        "services": [],
        "is_gateway": False,
    }


def _update_device(
    device: dict[str, Any], host: dict[str, Any], scan: dict[str, Any], network_key: str
) -> None:
    mac = _normalise_mac(host.get("mac"))
    display_names = {
        item.get("value", "").strip()
        for item in host.get("names") or []
        if item.get("value")
    }
    if host.get("name"):
        display_names.add(host["name"].strip())

    device["last_seen_utc"] = scan["timestamp_utc"]
    device["observation_count"] = int(device.get("observation_count") or 0) + 1
    device["network_key"] = network_key
    device["last_scan_id"] = scan.get("id")
    device["last_ip"] = host.get("ip")
    device["name"] = host.get("name")
    device["known_names"] = sorted(
        set(device.get("known_names") or []).union(display_names), key=str.casefold
    )
    device["manufacturer"] = host.get("manufacturer")
    device["model"] = host.get("model")
    device["confidence"] = host.get("confidence")
    device["evidence"] = list(host.get("evidence") or [])
    device["services"] = list(host.get("services") or [])
    device["is_gateway"] = bool((host.get("flags") or {}).get("G"))
    if mac:
        device["mac"] = mac
        device["identity_basis"] = "mac"
    elif device.get("identity_basis") != "mac":
        device["identity_basis"] = "network_ip"


def reconcile_inventory(inventory: dict[str, Any], scan: dict[str, Any]) -> dict[str, Any]:
    result = {"version": 1, "devices": list(inventory.get("devices") or [])}
    network_key = _network_key(scan)
    for host in scan.get("hosts") or []:
        device = _find_device(result["devices"], host, network_key)
        if device is None:
            device = _new_device(host, scan, network_key)
            result["devices"].append(device)
        _update_device(device, host, scan, network_key)

    result["devices"].sort(
        key=lambda item: (item.get("last_seen_utc", ""), item.get("id", "")), reverse=True
    )
    return result


def seed_inventory_from_history(
    inventory: dict[str, Any], history: dict[str, Any]
) -> dict[str, Any]:
    if inventory.get("devices"):
        return inventory
    for scan in reversed(history.get("scans") or []):
        if scan.get("hosts") and scan.get("timestamp_utc"):
            return reconcile_inventory(inventory, scan)
    return inventory


def update_user_label(
    inventory: dict[str, Any], device_id: str, label: str | None
) -> dict[str, Any] | None:
    cleaned = (label or "").strip() or None
    for device in inventory.get("devices") or []:
        if device.get("id") == device_id:
            device["user_label"] = cleaned
            return device
    return None
