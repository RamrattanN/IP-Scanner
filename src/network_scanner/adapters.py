from __future__ import annotations

import re
import socket
import subprocess
import sys

import psutil

def _get_windows_gateways() -> dict[str, str]:
    """Returns {interface_name: default_gateway_ipv4} by parsing ipconfig."""
    try:
        out = subprocess.check_output(["ipconfig"], text=True, encoding="utf-8", errors="ignore")
    except Exception:
        return {}
    gw_by_if: dict[str, str] = {}
    current_if = None
    for line in out.splitlines():
        if line.strip().endswith(":") and ("adapter" in line.lower()):
            current_if = line.strip().rstrip(":").split("adapter", 1)[-1].strip()
            continue
        if "Default Gateway" in line:
            m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if current_if and m:
                gw_by_if[current_if] = m.group(1)
    return gw_by_if


def _get_macos_gateways() -> dict[str, str]:
    """Return the active default route as {interface_name: gateway_ipv4}."""
    try:
        out = subprocess.check_output(
            ["route", "-n", "get", "default"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return {}
    interface = re.search(r"^\s*interface:\s*(\S+)", out, re.MULTILINE)
    gateway = re.search(r"^\s*gateway:\s*(\d+\.\d+\.\d+\.\d+)", out, re.MULTILINE)
    if interface and gateway:
        return {interface.group(1): gateway.group(1)}
    return {}


def _get_linux_gateways() -> dict[str, str]:
    try:
        out = subprocess.check_output(
            ["ip", "route", "show", "default"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return {}
    match = re.search(r"\bvia\s+(\d+\.\d+\.\d+\.\d+)\s+dev\s+(\S+)", out)
    if match:
        return {match.group(2): match.group(1)}
    return {}


def get_default_gateways(platform: str | None = None) -> dict[str, str]:
    platform = platform or sys.platform
    if platform == "win32":
        return _get_windows_gateways()
    if platform == "darwin":
        return _get_macos_gateways()
    return _get_linux_gateways()


def detect_active_adapter():
    addrs = psutil.net_if_addrs()
    candidates = []
    for name, lst in addrs.items():
        ipv4 = next((a.address for a in lst if a.family == socket.AF_INET and not a.address.startswith("127.")), None)
        netmask = next((a.netmask for a in lst if a.family == socket.AF_INET), None)
        if ipv4:
            candidates.append({"name": name, "ipv4": ipv4, "netmask": netmask, "gateway": None, "ssid": None})
    if not candidates:
        return None
    gws = get_default_gateways()
    for c in candidates:
        match = next(
            (
                gw
                for ifname, gw in gws.items()
                if ifname.casefold() == c["name"].casefold()
                or ifname.casefold() in c["name"].casefold()
            ),
            None,
        )
        if match:
            c["gateway"] = match
            return c
    for c in candidates:
        if any(c["ipv4"].startswith(prefix) for prefix in ("10.", "172.", "192.168.")):
            return c
    return candidates[0]
