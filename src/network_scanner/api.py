from __future__ import annotations
import ipaddress
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .storage import load_history, save_history, get_app_data_dir, new_scan_record
from .adapters import detect_active_adapter
from .cidr import cidr_from_adapter, cidr_to_range
from .scanner import Scanner, ScannerConfig
from .device_types import classify_device_type
from .discovery import format_mac_address, is_valid_unicast_mac
from .vendors import lookup_mac_vendor

router = APIRouter()
MAX_ADDRESSES = 4096

class StartScanRequest(BaseModel):
    start_ip: Optional[str] = None
    end_ip: Optional[str] = None
    network_name: Optional[str] = None

@router.get("/ping")
def ping() -> Dict[str, str]:
    return {"status": "ok"}

@router.get("/history")
def get_history() -> Dict[str, Any]:
    history = load_history(get_app_data_dir())
    for scan in history.get("scans") or []:
        for host in scan.get("hosts") or []:
            formatted_mac = format_mac_address(host.get("mac"))
            host["mac"] = formatted_mac if is_valid_unicast_mac(formatted_mac) else None
            notes = host.setdefault("notes", {})
            if notes.get("shared_proxy_mac"):
                notes["shared_proxy_mac"] = format_mac_address(notes["shared_proxy_mac"])
            if not host.get("manufacturer") and host.get("mac"):
                host["manufacturer"] = lookup_mac_vendor(host["mac"])
                if host["manufacturer"]:
                    notes["manufacturer_source"] = "IEEE OUI"
            host["device_type"] = classify_device_type(host)
    return history

@router.post("/clear-history")
def clear_history() -> Dict[str, Any]:
    # Replace with empty structure
    data = {"version": 1, "scans": []}
    save_history(get_app_data_dir(), data)
    return {"cleared": True}

@router.post("/start-scan")
async def start_scan(req: StartScanRequest) -> Dict[str, Any]:
    adapter = detect_active_adapter()
    if not adapter:
        raise HTTPException(status_code=400, detail="No active adapter detected")

    cidr = cidr_from_adapter(adapter)
    start, end = cidr_to_range(cidr)
    if (req.start_ip is None) != (req.end_ip is None):
        raise HTTPException(status_code=422, detail="Provide both a starting and ending IPv4 address")
    start_ip = req.start_ip or start
    end_ip = req.end_ip or end
    try:
        start_address = ipaddress.IPv4Address(start_ip)
        end_address = ipaddress.IPv4Address(end_ip)
    except ipaddress.AddressValueError as exc:
        raise HTTPException(status_code=422, detail="Enter valid IPv4 addresses") from exc
    if end_address < start_address:
        raise HTTPException(status_code=422, detail="The ending address must not precede the starting address")
    address_count = int(end_address) - int(start_address) + 1
    if address_count > MAX_ADDRESSES:
        raise HTTPException(
            status_code=422,
            detail=f"This build accepts at most {MAX_ADDRESSES} addresses in one scan",
        )
    name = req.network_name or adapter.get("ssid") or adapter.get("name") or cidr

    # Prepare scan record
    app_dir = get_app_data_dir()
    record = new_scan_record(name, cidr, start_ip, end_ip, adapter)

    # Persist early with empty hosts list
    history = load_history(app_dir)
    history["scans"].append(record)
    save_history(app_dir, history)

    # Kick off scanner (synchronous placeholder, to be replaced with background task or websocket updates)
    cfg = ScannerConfig()
    scanner = Scanner(cfg)
    result = await scanner.run(record)

    # Replace the last record with final result
    history = load_history(app_dir)
    history["scans"] = [result if item.get("id") == result["id"] else item for item in history["scans"]]
    save_history(app_dir, history)
    return {"started": True, "scan_id": result["id"], "stats": result["stats"]}
