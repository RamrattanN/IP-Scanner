from __future__ import annotations
import json, os, datetime
from pathlib import Path

def get_app_data_dir() -> Path:
    configured = os.environ.get("IP_SCANNER_DATA_DIR")
    if configured:
        data_dir = Path(configured).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    home = Path.home()
    docs = home / "Documents" / "Network Scanner"
    docs.mkdir(parents=True, exist_ok=True)
    return docs

def history_path(base_dir: Path) -> Path:
    return base_dir / "history.json"

def settings_path(base_dir: Path) -> Path:
    return base_dir / "settings.json"

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

def load_settings(base_dir: Path) -> dict:
    p = settings_path(base_dir)
    defaults = {"version": 1, "automatic_scans": True, "interval_minutes": 60}
    if not p.exists():
        save_settings(base_dir, defaults)
        return defaults
    try:
        with open(p, "r", encoding="utf-8") as f:
            saved = json.load(f)
    except (OSError, json.JSONDecodeError):
        return defaults
    return {**defaults, **saved}

def save_settings(base_dir: Path, data: dict) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    p = settings_path(base_dir)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, p)

def new_scan_record(network_name: str, cidr: str, start_ip: str, end_ip: str, adapter: dict) -> dict:
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
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
            "confirmed_devices": 0,
            "observed_devices": 0,
            "ping_replies": 0,
            "neighbor_only": 0,
            "proxy_arp_ignored": 0,
            "reserved_ignored": 0,
            "website": 0,
            "upnp": 0,
            "bonjour": 0,
            "ipv6": 0,
            "duration_ms": 0,
            "cancelled": False,
        },
        "hosts": [],
    }
