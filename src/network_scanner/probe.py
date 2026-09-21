from __future__ import annotations

import asyncio
import math
import sys
from typing import Dict, Any

import httpx


def ping_command(ip: str, timeout_ms: int = 400, platform: str | None = None) -> list[str]:
    """Build the native one-packet ping command for a supported platform."""
    platform = platform or sys.platform
    if platform == "win32":
        return ["ping", "-n", "1", "-w", str(timeout_ms), ip]
    if platform == "darwin":
        return ["ping", "-n", "-c", "1", "-W", str(timeout_ms), ip]
    timeout_seconds = max(1, math.ceil(timeout_ms / 1000))
    return ["ping", "-n", "-c", "1", "-W", str(timeout_seconds), ip]


async def _ping(ip: str, timeout_ms: int = 400) -> bool:
    try:
        proc = await asyncio.create_subprocess_exec(
            *ping_command(ip, timeout_ms),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        rc = await proc.wait()
        return rc == 0
    except Exception:
        return False

async def _http_head(url: str, timeout: float = 0.6) -> bool:
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            r = await client.head(url, follow_redirects=True)
            return r.status_code < 500
    except Exception:
        return False

async def probe_host(ip: str) -> Dict[str, Any]:
    flags = {"G": False, "W": False, "U": False, "B": False, "P": False, "6": False}
    notes: Dict[str, Any] = {}
    reachable = await _ping(ip)
    flags["P"] = reachable
    if reachable:
        if await _http_head(f"http://{ip}") or await _http_head(f"https://{ip}"):
            flags["W"] = True
    name = None
    return {
        "ip": ip,
        "name": name,
        "reachable": reachable,
        "flags": flags,
        "notes": notes,
    }
