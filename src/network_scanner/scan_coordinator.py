from __future__ import annotations

import asyncio
import datetime as dt
import ipaddress
import logging
from pathlib import Path
from typing import Any

from .adapters import detect_active_adapter
from .cidr import cidr_from_adapter, cidr_to_range
from .scanner import Scanner, ScannerConfig
from .storage import load_history, load_settings, new_scan_record, save_history

MAX_ADDRESSES = 4096
MIN_INTERVAL_MINUTES = 5
MAX_INTERVAL_MINUTES = 1440
logger = logging.getLogger(__name__)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_utc(value: dt.datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_timestamp(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class ScanConflictError(RuntimeError):
    pass


class ScanValidationError(ValueError):
    pass


class ScanCoordinator:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._scheduler_task: asyncio.Task[None] | None = None
        self.running = False
        self.source: str | None = None
        self.started_at: dt.datetime | None = None
        self.last_completed_at: dt.datetime | None = None
        self.last_error: str | None = None
        self.next_run_at: dt.datetime | None = None

    def status(self, app_dir: Path) -> dict[str, Any]:
        settings = load_settings(app_dir)
        history = load_history(app_dir)
        scans = history.get("scans") or []
        for scan in reversed(scans):
            recorded_value = scan.get("completed_at_utc")
            if not recorded_value and "trigger" not in scan:
                recorded_value = scan.get("timestamp_utc")
            recorded = parse_timestamp(recorded_value)
            if recorded and (self.last_completed_at is None or recorded > self.last_completed_at):
                self.last_completed_at = recorded
            if recorded:
                break
        interval = int(settings["interval_minutes"])
        age_seconds = None
        freshness = "never"
        if self.last_completed_at:
            age_seconds = max(0, int((utc_now() - self.last_completed_at).total_seconds()))
            if age_seconds <= interval * 60:
                freshness = "fresh"
            elif age_seconds <= interval * 120:
                freshness = "aging"
            else:
                freshness = "stale"
        if self.running:
            freshness = "scanning"
        return {
            "running": self.running,
            "source": self.source,
            "started_at_utc": iso_utc(self.started_at),
            "last_completed_at_utc": iso_utc(self.last_completed_at),
            "next_run_at_utc": iso_utc(self.next_run_at) if settings["automatic_scans"] else None,
            "last_error": self.last_error,
            "freshness": freshness,
            "age_seconds": age_seconds,
        }

    async def run_scan(
        self,
        app_dir: Path,
        *,
        start_ip: str | None = None,
        end_ip: str | None = None,
        network_name: str | None = None,
        source: str = "manual",
    ) -> dict[str, Any]:
        if self._lock.locked():
            raise ScanConflictError("A scan is already in progress")
        async with self._lock:
            self.running = True
            self.source = source
            self.started_at = utc_now()
            self.last_error = None
            record: dict[str, Any] | None = None
            try:
                adapter = detect_active_adapter()
                if not adapter:
                    raise ScanValidationError("No active adapter detected")
                cidr = cidr_from_adapter(adapter)
                detected_start, detected_end = cidr_to_range(cidr)
                if (start_ip is None) != (end_ip is None):
                    raise ScanValidationError("Provide both a starting and ending IPv4 address")
                scan_start = start_ip or detected_start
                scan_end = end_ip or detected_end
                try:
                    start_address = ipaddress.IPv4Address(scan_start)
                    end_address = ipaddress.IPv4Address(scan_end)
                except ipaddress.AddressValueError as exc:
                    raise ScanValidationError("Enter valid IPv4 addresses") from exc
                if end_address < start_address:
                    raise ScanValidationError("The ending address must not precede the starting address")
                count = int(end_address) - int(start_address) + 1
                if count > MAX_ADDRESSES:
                    raise ScanValidationError(
                        f"This build accepts at most {MAX_ADDRESSES} addresses in one scan"
                    )
                name = network_name or adapter.get("ssid") or adapter.get("name") or cidr
                record = new_scan_record(name, cidr, scan_start, scan_end, adapter)
                record["trigger"] = source
                record["state"] = "running"
                history = load_history(app_dir)
                history["scans"].append(record)
                save_history(app_dir, history)
                result = await Scanner(ScannerConfig()).run(record)
                completed = utc_now()
                result["completed_at_utc"] = iso_utc(completed)
                result["state"] = "completed"
                history = load_history(app_dir)
                history["scans"] = [
                    result if item.get("id") == result["id"] else item
                    for item in history["scans"]
                ]
                save_history(app_dir, history)
                self.last_completed_at = completed
                self._schedule_next(app_dir, completed)
                return result
            except Exception as exc:
                self.last_error = str(exc)
                if record is not None:
                    history = load_history(app_dir)
                    for item in history["scans"]:
                        if item.get("id") == record["id"]:
                            item["state"] = "failed"
                            item["error"] = str(exc)
                    save_history(app_dir, history)
                raise
            finally:
                self.running = False
                self.source = None
                self.started_at = None

    def _schedule_next(self, app_dir: Path, from_time: dt.datetime | None = None) -> None:
        settings = load_settings(app_dir)
        if settings["automatic_scans"]:
            self.next_run_at = (from_time or utc_now()) + dt.timedelta(
                minutes=int(settings["interval_minutes"])
            )
        else:
            self.next_run_at = None

    def settings_changed(self, app_dir: Path) -> None:
        self._schedule_next(app_dir)

    async def start_scheduler(self, app_dir: Path) -> None:
        if self._scheduler_task and not self._scheduler_task.done():
            return
        self.status(app_dir)
        settings = load_settings(app_dir)
        if settings["automatic_scans"]:
            if self.last_completed_at:
                due = self.last_completed_at + dt.timedelta(minutes=int(settings["interval_minutes"]))
                self.next_run_at = max(due, utc_now())
            else:
                self.next_run_at = utc_now() + dt.timedelta(seconds=10)
        self._scheduler_task = asyncio.create_task(self._scheduler_loop(app_dir))

    async def stop_scheduler(self) -> None:
        if not self._scheduler_task:
            return
        self._scheduler_task.cancel()
        try:
            await self._scheduler_task
        except asyncio.CancelledError:
            pass
        self._scheduler_task = None

    async def _scheduler_loop(self, app_dir: Path) -> None:
        while True:
            await asyncio.sleep(2)
            settings = load_settings(app_dir)
            if not settings["automatic_scans"]:
                self.next_run_at = None
                continue
            if self.next_run_at is None:
                self._schedule_next(app_dir)
            if self.next_run_at and utc_now() >= self.next_run_at and not self._lock.locked():
                try:
                    await self.run_scan(app_dir, source="scheduled")
                except Exception:
                    logger.exception("Scheduled scan failed")
                    self._schedule_next(app_dir)


coordinator = ScanCoordinator()
