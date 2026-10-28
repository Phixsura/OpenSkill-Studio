"""App Maintenance Window — schedule and manage maintenance windows.

Manages scheduled maintenance for installed apps:
- Create windows with start/end times
- Track maintenance status (scheduled, active, completed, cancelled)
- Affected service listing
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
    """A scheduled maintenance window."""

    window_id: str
    installation_id: str
    title: str
    description: str
    start_at: float
    end_at: float
    status: WindowStatus = WindowStatus.SCHEDULED
    affected_services: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class AppMaintenanceWindow:
    """Schedule and manage maintenance windows."""

    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], MaintenanceWindow] = {}

    def schedule(
        self,
        installation_id: str,
        window_id: str,
        title: str,
        description: str,
        start_at: float,
        end_at: float,
        affected_services: list[str] | None = None,
    ) -> MaintenanceWindow:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not window_id:
            raise ValueError("window_id is required")
        if not title:
            raise ValueError("title is required")
        if end_at <= start_at:
            raise ValueError("end_at must be after start_at")

        key = (installation_id, window_id)
        if key in self._windows:
            raise ValueError(f"Window {window_id} already exists")

        window = MaintenanceWindow(
            window_id=window_id, installation_id=installation_id,
            title=title, description=description,
            start_at=start_at, end_at=end_at,
            affected_services=affected_services or [],
        )
        self._windows[key] = window
        return window

    def activate(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        w = self._get(installation_id, window_id)
        if w.status != WindowStatus.SCHEDULED:
            raise ValueError(f"Cannot activate window in {w.status} state")
        w.status = WindowStatus.ACTIVE
        return w

    def complete(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        w = self._get(installation_id, window_id)
        if w.status != WindowStatus.ACTIVE:
            raise ValueError(f"Cannot complete window in {w.status} state")
        w.status = WindowStatus.COMPLETED
        return w

    def cancel(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        w = self._get(installation_id, window_id)
        if w.status in (WindowStatus.COMPLETED, WindowStatus.CANCELLED):
            raise ValueError(f"Cannot cancel window in {w.status} state")
        w.status = WindowStatus.CANCELLED
        return w

    def is_in_maintenance(self, installation_id: str, now: float | None = None) -> bool:
        now = now or time.time()
        return any(
            w.status == WindowStatus.ACTIVE
            for (inst, _), w in self._windows.items()
            if inst == installation_id
        )

    def get_upcoming(self, installation_id: str, limit: int = 10) -> list[MaintenanceWindow]:
        windows = [
            w for (inst, _), w in self._windows.items()
            if inst == installation_id and w.status == WindowStatus.SCHEDULED
        ]
        return sorted(windows, key=lambda w: w.start_at)[:limit]

    def list_windows(self, installation_id: str) -> list[MaintenanceWindow]:
        return [w for (inst, _), w in self._windows.items() if inst == installation_id]

    def _get(self, installation_id: str, window_id: str) -> MaintenanceWindow:
        key = (installation_id, window_id)
        w = self._windows.get(key)
        if w is None:
            raise KeyError(f"Window {window_id} not found")
        return w
