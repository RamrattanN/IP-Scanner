from __future__ import annotations
import json, os, datetime, uuid
from pathlib import Path

def get_app_data_dir() -> Path:
    home = Path.home()
    docs = home / "Documents" / "Network Scanner"
    docs.mkdir(parents=True, exist_ok=True)
    return docs

def history_path(base_dir: Path) -> Path:
    return base_dir / "history.json"

def ensure_history_file(base_dir: Path) -> None:
    p = history_path(base_dir)
    if not p.exists():
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "scans": []}, f, indent=2)

def load_history(base_dir: Path) -> dict:
    p = history_path(base_dir)
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(base_dir: Path, data: dict) -> None:
    p = history_path(base_dir)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, p)

def new_scan_record(network_name: str, cidr: str, start_ip: str, end_ip: str, adapter: dict) -> dict:
    ts = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    scan_id = f"{ts}_{cidr.replace('/', '_')}"
    return {
        "id": scan_id,
        "timestamp_utc": ts,
        "network_name": network_name,
        "cidr": cidr,
        "range": {"start": start_ip, "end": end_ip},
        "adapter": adapter,
        "stats": {
            "addresses_requested": 0,
            "addresses_attempted": 0,
            "probe_errors": 0,
            "hosts_up": 0,
            "ping_replies": 0,
            "neighbor_only": 0,
            "website": 0,
            "upnp": 0,
            "bonjour": 0,
            "ipv6": 0,
            "duration_ms": 0,
            "cancelled": False,
        },
        "hosts": [],
    }
