from __future__ import annotations

import asyncio
import errno
import logging
import math
import re
import socket
import sys
from typing import Any, Dict

import httpx


logger = logging.getLogger(__name__)


# Common computer, router, printer, NAS, camera, and local web-service ports.
# Connection attempts also populate the operating system's neighbor table.
TCP_SERVICES = {
    22: "SSH",
    53: "DNS",
    80: "HTTP",
    139: "NetBIOS",
    443: "HTTPS",
    445: "SMB",
    515: "LPD",
    631: "IPP",
    3389: "RDP",
    5000: "Web 5000",
    8000: "Web 8000",
    8080: "Web 8080",
    8443: "Web 8443",
    9100: "JetDirect",
}
WEB_PORTS = {80, 443, 5000, 8000, 8080, 8443}


def ping_command(ip: str, timeout_ms: int = 500, platform: str | None = None) -> list[str]:
    """Build the native one-packet ping command for a supported platform."""
    platform = platform or sys.platform
    if platform == "win32":
        return ["ping", "-n", "1", "-w", str(timeout_ms), ip]
    if platform == "darwin":
        # Finder-launched applications receive a smaller and less predictable
        # PATH than interactive shells.  Use the stable macOS system path.
        return ["/sbin/ping", "-n", "-c", "1", "-W", str(timeout_ms), ip]
    timeout_seconds = max(1, math.ceil(timeout_ms / 1000))
    return ["ping", "-n", "-c", "1", "-W", str(timeout_seconds), ip]


async def _ping(ip: str, timeout_ms: int = 500) -> bool:
    try:
        proc = await asyncio.create_subprocess_exec(
            *ping_command(ip, timeout_ms),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        return await proc.wait() == 0
    except (OSError, asyncio.SubprocessError) as exc:
        logger.warning("ICMP probe failed for %s: %s: %s", ip, type(exc).__name__, exc)
        return False


TCP_OPEN = "open"
TCP_RESPONDED = "responded"
TCP_NO_RESPONSE = "no_response"
TCP_RESPONSE_ERRNOS = {errno.ECONNREFUSED, errno.ECONNRESET}


async def _tcp_probe(ip: str, port: int, timeout: float = 0.45) -> str:
    """Return whether a TCP port opened, rejected, or did not answer.

    A refusal or reset is not an open service, but it proves that the target
    address responded.  Keeping those states separate avoids both missed
    devices and false open-port claims.
    """
    writer = None
    try:
        _reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
        return TCP_OPEN
    except asyncio.TimeoutError:
        return TCP_NO_RESPONSE
    except ConnectionRefusedError:
        return TCP_RESPONDED
    except OSError as exc:
        return TCP_RESPONDED if exc.errno in TCP_RESPONSE_ERRNOS else TCP_NO_RESPONSE
    finally:
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except (OSError, RuntimeError):
                pass


def _send_udp_stimulus(ip: str) -> None:
    """Prompt local neighbor resolution without treating UDP as a reply."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.setblocking(False)
        sock.sendto(b"", (ip, 9))
    except OSError:
        pass
    finally:
        sock.close()


async def _reverse_dns(ip: str) -> str | None:
    try:
        host, _aliases, _addresses = await asyncio.wait_for(
            asyncio.to_thread(socket.gethostbyaddr, ip), timeout=1.0
        )
        return host.rstrip(".") or None
    except (OSError, asyncio.TimeoutError):
        return None


async def _web_identity(ip: str, open_ports: list[int]) -> dict[str, str]:
    """Read small, non-authenticated web metadata without retaining page content."""
    for port in open_ports:
        if port not in WEB_PORTS:
            continue
        scheme = "https" if port in {443, 8443} else "http"
        default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
        authority = ip if default_port else f"{ip}:{port}"
        try:
            async with httpx.AsyncClient(
                timeout=0.9, verify=False, follow_redirects=True, trust_env=False
            ) as client:
                async with client.stream("GET", f"{scheme}://{authority}/") as response:
                    server = response.headers.get("server", "").strip()
                    body = b""
                    async for chunk in response.aiter_bytes():
                        body += chunk
                        if len(body) >= 65536:
                            break
            text = body[:65536].decode("utf-8", errors="replace")
            title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
            title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
            return {
                key: value
                for key, value in {"web_title": title, "http_server": server}.items()
                if value
            }
        except (httpx.HTTPError, OSError):
            continue
    return {}


async def probe_host(
    ip: str,
    *,
    tcp_semaphore: asyncio.Semaphore | None = None,
) -> Dict[str, Any]:
    """Interrogate one IPv4 address and retain the evidence that answered."""
    flags = {"G": False, "W": False, "U": False, "B": False, "P": False, "6": False}

    _send_udp_stimulus(ip)
    ping_task = asyncio.create_task(_ping(ip))
    ports = tuple(TCP_SERVICES)

    async def limited_tcp_probe(port: int) -> str:
        if tcp_semaphore is None:
            return await _tcp_probe(ip, port)
        async with tcp_semaphore:
            return await _tcp_probe(ip, port)

    port_results = await asyncio.gather(*(limited_tcp_probe(port) for port in ports))
    pingable = await ping_task
    open_ports = [
        port for port, state in zip(ports, port_results) if state == TCP_OPEN
    ]
    tcp_responded = any(state in {TCP_OPEN, TCP_RESPONDED} for state in port_results)
    reachable = pingable or tcp_responded

    flags["P"] = pingable
    flags["W"] = any(port in WEB_PORTS for port in open_ports)
    evidence = []
    if pingable:
        evidence.append("ICMP")
    if tcp_responded:
        evidence.append("TCP")

    name = await _reverse_dns(ip) if reachable else None
    web_identity = await _web_identity(ip, open_ports) if open_ports else {}
    return {
        "ip": ip,
        "name": name,
        "names": ([{"source": "Reverse DNS", "value": name}] if name else []),
        "manufacturer": None,
        "model": None,
        "mac": None,
        "reachable": reachable,
        "evidence": evidence,
        "open_ports": open_ports,
        "services": [TCP_SERVICES[port] for port in open_ports],
        "flags": flags,
        "notes": web_identity,
    }
