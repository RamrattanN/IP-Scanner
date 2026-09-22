from __future__ import annotations

import re
import logging
import subprocess
import sys


IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
MAC_RE = re.compile(r"\b(?:[0-9a-f]{1,2}[:-]){5}[0-9a-f]{1,2}\b", re.IGNORECASE)
logger = logging.getLogger(__name__)


def neighbor_command(platform: str | None = None) -> list[str]:
    platform = platform or sys.platform
    if platform == "win32":
        return ["arp", "-a"]
    if platform == "darwin":
        return ["/usr/sbin/arp", "-an"]
    return ["arp", "-an"]


def parse_neighbor_table(output: str) -> dict[str, str]:
    """Parse complete IPv4-to-MAC entries from macOS, Windows, or Linux arp output."""
    neighbors: dict[str, str] = {}
    for line in output.splitlines():
        ip_match = IPV4_RE.search(line)
        mac_match = MAC_RE.search(line)
        if not ip_match or not mac_match:
            continue
        octets = ip_match.group(0).split(".")
        if any(int(octet) > 255 for octet in octets):
            continue
        mac = mac_match.group(0).replace("-", ":")
        mac = ":".join(part.zfill(2) for part in mac.split(":"))
        neighbors[ip_match.group(0)] = mac.upper()
    return neighbors


def get_neighbor_table(platform: str | None = None) -> dict[str, str]:
    try:
        output = subprocess.check_output(
            neighbor_command(platform), text=True, encoding="utf-8", errors="ignore"
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.warning("Neighbor-table read failed: %s: %s", type(exc).__name__, exc)
        return {}
    return parse_neighbor_table(output)
