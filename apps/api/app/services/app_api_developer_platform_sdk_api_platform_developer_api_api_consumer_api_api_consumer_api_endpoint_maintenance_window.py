"""Endpoint Maintenance Window — schedule downtime windows for endpoints."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class MaintenanceWindow:
    window_id: str
    endpoint_path: str
    starts_at: datetime
    ends_at: datetime
    reason: str = ""
    notify_consumers: bool = True
    status: str = "scheduled"  # "scheduled", "active", "completed", "cancelled"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindow:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], MaintenanceWindow] = {}

    def schedule(self, installation_id: str, window: MaintenanceWindow) -> MaintenanceWindow:
        if not installation_id:
            raise ValueError("installation_id is required")
        if window.ends_at <= window.starts_at:
            raise ValueError("ends_at must be after starts_at")
        key = (installation_id, window.window_id)
        if key in self._windows:
            raise ValueError(f"Window {window.window_id} already exists")
        window.status = "scheduled"
        self._windows[key] = window
        log.info("maintenance_scheduled", installation_id=installation_id, path=window.endpoint_path, starts=window.starts_at.isoformat())
        return window

    def cancel(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        key = (installation_id, window_id)
        w = self._windows.get(key)
        if not w:
            raise ValueError("Window not found")
        if w.status == "completed":
            raise ValueError("Cannot cancel completed window")
        w.status = "cancelled"
        return w

    def is_in_maintenance(self, installation_id: str, endpoint_path: str, now: datetime) -> MaintenanceWindow | None:
        for (inst, _), w in self._windows.items():
            if inst == installation_id and w.endpoint_path == endpoint_path and w.status != "cancelled" and w.starts_at <= now < w.ends_at:
                return w
        return None

    def update_statuses(self, installation_id: str, now: datetime) -> int:
        updated = 0
        for (inst, _), w in self._windows.items():
            if inst != installation_id:
                continue
            if w.status == "scheduled" and now >= w.starts_at:
                w.status = "active"
                updated += 1
            elif w.status == "active" and now >= w.ends_at:
                w.status = "completed"
                updated += 1
        return updated

    def upcoming(self, installation_id: str, now: datetime) -> list[MaintenanceWindow]:
        return sorted([w for (inst, _), w in self._windows.items() if inst == installation_id and w.status == "scheduled" and w.starts_at > now], key=lambda w: w.starts_at)

    def list_all(self, installation_id: str) -> list[MaintenanceWindow]:
        return [w for (inst, _), w in self._windows.items() if inst == installation_id]
