from __future__ import annotations
import asyncio, subprocess
from typing import Dict, Any
import httpx

async def _ping_win(ip: str, timeout_ms: int = 400) -> bool:
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping", "-n", "1", "-w", str(timeout_ms), ip,
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
    reachable = await _ping_win(ip)
    flags["P"] = reachable
    if reachable:
        if await _http_head(f"http://{ip}") or await _http_head(f"https://{ip}"):
            flags["W"] = True
    name = None
    return {"ip": ip, "name": name, "flags": flags, "notes": notes}
