from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .device_intelligence import infer_identity_from_direct_vendor
from .device_types import classify_device_type
from .discovery import format_mac_address, is_valid_unicast_mac
from .scan_coordinator import (
    MAX_INTERVAL_MINUTES,
    MIN_INTERVAL_MINUTES,
    ScanConflictError,
    ScanValidationError,
    coordinator,
)
from .storage import get_app_data_dir, load_history, load_settings, save_history, save_settings
from .vendors import lookup_mac_vendor

router = APIRouter()


class StartScanRequest(BaseModel):
    start_ip: Optional[str] = None
    end_ip: Optional[str] = None
    network_name: Optional[str] = None


class ScheduleRequest(BaseModel):
    enabled: bool
    interval_minutes: int = Field(ge=MIN_INTERVAL_MINUTES, le=MAX_INTERVAL_MINUTES)


@router.get("/ping")
def ping() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/history")
def get_history() -> Dict[str, Any]:
    history = load_history(get_app_data_dir())
    history["scans"] = [
        scan for scan in history.get("scans") or []
        if scan.get("state") in (None, "completed")
    ]
    for scan in history.get("scans") or []:
        for host in scan.get("hosts") or []:
            formatted_mac = format_mac_address(host.get("mac"))
            host["mac"] = formatted_mac if is_valid_unicast_mac(formatted_mac) else None
            notes = host.setdefault("notes", {})
            if notes.get("shared_proxy_mac"):
                notes["shared_proxy_mac"] = format_mac_address(notes["shared_proxy_mac"])
                notes["shared_proxy_vendor"] = lookup_mac_vendor(notes["shared_proxy_mac"])
            if host.get("mac"):
                host["mac_vendor"] = lookup_mac_vendor(host["mac"])
            if not host.get("manufacturer") and host.get("mac_vendor"):
                host["manufacturer"] = host["mac_vendor"]
                if host.get("manufacturer"):
                    notes["manufacturer_source"] = "IEEE OUI"
            infer_identity_from_direct_vendor(host)
            host["device_type"] = classify_device_type(host)
    return history


@router.post("/clear-history")
def clear_history() -> Dict[str, Any]:
    if coordinator.running:
        raise HTTPException(status_code=409, detail="A scan is already in progress")
    save_history(get_app_data_dir(), {"version": 1, "scans": []})
    coordinator.last_completed_at = None
    return {"cleared": True}


@router.get("/scan-status")
def scan_status() -> Dict[str, Any]:
    return coordinator.status(get_app_data_dir())


@router.get("/schedule")
def get_schedule() -> Dict[str, Any]:
    settings = load_settings(get_app_data_dir())
    return {
        "enabled": bool(settings["automatic_scans"]),
        "interval_minutes": int(settings["interval_minutes"]),
    }


@router.put("/schedule")
def update_schedule(req: ScheduleRequest) -> Dict[str, Any]:
    app_dir = get_app_data_dir()
    settings = load_settings(app_dir)
    settings.update(automatic_scans=req.enabled, interval_minutes=req.interval_minutes)
    save_settings(app_dir, settings)
    coordinator.settings_changed(app_dir)
    return {"enabled": req.enabled, "interval_minutes": req.interval_minutes}


@router.post("/start-scan")
async def start_scan(req: StartScanRequest) -> Dict[str, Any]:
    try:
        result = await coordinator.run_scan(
            get_app_data_dir(),
            start_ip=req.start_ip,
            end_ip=req.end_ip,
            network_name=req.network_name,
            source="manual",
        )
    except ScanConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ScanValidationError as exc:
        status_code = 400 if "adapter" in str(exc).lower() else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return {"started": True, "scan_id": result["id"], "stats": result["stats"]}
