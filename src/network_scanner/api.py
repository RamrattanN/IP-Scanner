from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .storage import load_history, save_history, get_app_data_dir, new_scan_record
from .adapters import detect_active_adapter
from .cidr import cidr_from_adapter, cidr_to_range
from .scanner import Scanner, ScannerConfig

router = APIRouter()

class StartScanRequest(BaseModel):
    start_ip: Optional[str] = None
    end_ip: Optional[str] = None
    network_name: Optional[str] = None

@router.get("/ping")
def ping() -> Dict[str, str]:
    return {"status": "ok"}

@router.get("/history")
def get_history() -> Dict[str, Any]:
    return load_history(get_app_data_dir())

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
    start_ip = req.start_ip or start
    end_ip = req.end_ip or end
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
    history["scans"][-1] = result
    save_history(app_dir, history)
    return {"started": True, "scan_id": result["id"]}
