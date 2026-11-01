"""App Maintenance Window — schedule and manage maintenance periods.

Manages maintenance windows:
- Schedule windows with start/end times
- Track active/upcoming/past windows
- Affected services list
- Per-installation scoped windows
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class WindowStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class MaintenanceWindow:
    """A maintenance window."""

    window_id: str
    title: str
    start_at: float
    end_at: float
    affected_services: list[str] = field(default_factory=list)
    status: WindowStatus = WindowStatus.SCHEDULED
    message: str = ""

    @property
    def duration_minutes(self) -> float:
        return round((self.end_at - self.start_at) / 60, 1)


class AppMaintenanceWindow:
    """Schedule and manage maintenance periods."""

    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], MaintenanceWindow] = {}

    def schedule(
        self, installation_id: str, window_id: str, title: str,
        start_at: float, end_at: float,
        affected_services: list[str] | None = None, message: str = "",
    ) -> MaintenanceWindow:
        if not installation_id:
            raise ValueError("installation_id is required")
        if end_at <= start_at:
            raise ValueError("end_at must be after start_at")

        window = MaintenanceWindow(
            window_id=window_id, title=title,
            start_at=start_at, end_at=end_at,
            affected_services=affected_services or [],
            message=message,
        )
        self._windows[(installation_id, window_id)] = window
        return window

    def activate(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        w = self._get(installation_id, window_id)
        if w.status != WindowStatus.SCHEDULED:
            raise ValueError("Window is not scheduled")
        w.status = WindowStatus.ACTIVE
        return w

    def complete(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        w = self._get(installation_id, window_id)
        if w.status != WindowStatus.ACTIVE:
            raise ValueError("Window is not active")
        w.status = WindowStatus.COMPLETED
        return w

    def cancel(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        w = self._get(installation_id, window_id)
        if w.status in (WindowStatus.COMPLETED, WindowStatus.CANCELLED):
            raise ValueError("Window already finished")
        w.status = WindowStatus.CANCELLED
        return w

    def is_in_maintenance(self, installation_id: str, service: str | None = None) -> bool:
        for (inst, _), w in self._windows.items():
            if inst != installation_id or w.status != WindowStatus.ACTIVE:
                continue
            if service is None or service in w.affected_services or not w.affected_services:
                return True
        return False

    def list_windows(self, installation_id: str, status: WindowStatus | None = None) -> list[MaintenanceWindow]:
        windows = [w for (inst, _), w in self._windows.items() if inst == installation_id]
        if status:
            windows = [w for w in windows if w.status == status]
        return windows

    def _get(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        key = (installation_id, window_id)
        w = self._windows.get(key)
        if w is None:
            raise KeyError(f"Window {window_id} not found")
        return w
