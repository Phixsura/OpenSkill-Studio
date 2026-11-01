"""App Data Export Schedule — schedule recurring data exports.

Manages recurring export schedules:
- Define export jobs with schedule and destination
- Track last run and next run
- Enable/disable schedules
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ExportSchedule:
    """A recurring data export schedule."""

    schedule_id: str
    resource_type: str
    format: str
    destination: str  # S3 URL, email, webhook
    interval_hours: int
    enabled: bool = True
    last_run_at: float | None = None
    next_run_at: float | None = None
    run_count: int = 0
    last_error: str = ""


class AppDataExportSchedule:
    """Schedule recurring data exports."""

    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str], ExportSchedule] = {}

    def create_schedule(
        self,
        installation_id: str,
        schedule_id: str,
        resource_type: str,
        fmt: str,
        destination: str,
        interval_hours: int,
        now: float | None = None,
    ) -> ExportSchedule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not schedule_id:
            raise ValueError("schedule_id is required")
        if interval_hours < 1:
            raise ValueError("interval_hours must be >= 1")
        if not destination:
            raise ValueError("destination is required")

        now = now or time.time()
        key = (installation_id, schedule_id)
        if key in self._schedules:
            raise ValueError(f"Schedule {schedule_id} already exists")

        sched = ExportSchedule(
            schedule_id=schedule_id, resource_type=resource_type,
            format=fmt, destination=destination,
            interval_hours=interval_hours,
            next_run_at=now + interval_hours * 3600,
        )
        self._schedules[key] = sched
        return sched

    def record_run(
        self, installation_id: str, schedule_id: str,
        success: bool = True, error: str = "", now: float | None = None,
    ) -> ExportSchedule:
        s = self._get(installation_id, schedule_id)
        now = now or time.time()
        s.last_run_at = now
        s.next_run_at = now + s.interval_hours * 3600
        s.run_count += 1
        s.last_error = error if not success else ""
        return s

    def get_due(self, installation_id: str, now: float | None = None) -> list[ExportSchedule]:
        now = now or time.time()
        return [
            s for (inst, _), s in self._schedules.items()
            if inst == installation_id and s.enabled
            and s.next_run_at is not None and now >= s.next_run_at
        ]

    def enable(self, installation_id: str, schedule_id: str) -> ExportSchedule:
        s = self._get(installation_id, schedule_id)
        s.enabled = True
        return s

    def disable(self, installation_id: str, schedule_id: str) -> ExportSchedule:
        s = self._get(installation_id, schedule_id)
        s.enabled = False
        return s

    def list_schedules(self, installation_id: str) -> list[ExportSchedule]:
        return [s for (inst, _), s in self._schedules.items() if inst == installation_id]

    def _get(self, installation_id: str, schedule_id: str) -> ExportSchedule:
        key = (installation_id, schedule_id)
        s = self._schedules.get(key)
        if s is None:
            raise KeyError(f"Schedule {schedule_id} not found")
        return s
