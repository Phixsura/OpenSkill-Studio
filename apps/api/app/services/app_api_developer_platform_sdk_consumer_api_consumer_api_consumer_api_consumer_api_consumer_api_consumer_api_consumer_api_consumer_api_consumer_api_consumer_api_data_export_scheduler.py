"""Consumer API Data Export Scheduler — schedule recurring data exports."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ExportSchedule:
    schedule_id: str
    consumer_id: str
    data_type: str  # "logs", "analytics", "usage", "audit"
    format: str = "json"  # "json", "csv", "ndjson"
    frequency: str = "daily"  # "daily", "weekly", "monthly"
    destination: str = ""  # email or webhook URL
    enabled: bool = True
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None

VALID_DATA_TYPES = {"logs", "analytics", "usage", "audit", "billing", "errors"}
VALID_FREQUENCIES = {"daily", "weekly", "monthly", "hourly"}

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiDataExportScheduler:
    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str, str], ExportSchedule] = {}

    def create(self, installation_id: str, schedule: ExportSchedule) -> ExportSchedule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if schedule.data_type not in VALID_DATA_TYPES:
            raise ValueError(f"Invalid data_type: {schedule.data_type}")
        if schedule.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"Invalid frequency: {schedule.frequency}")
        if schedule.format not in ("json", "csv", "ndjson"):
            raise ValueError(f"Invalid format: {schedule.format}")
        key = (installation_id, schedule.consumer_id, schedule.schedule_id)
        if key in self._schedules:
            raise ValueError(f"Schedule {schedule.schedule_id} already exists")
        self._schedules[key] = schedule
        return schedule

    def update(self, installation_id: str, consumer_id: str, schedule_id: str, enabled: bool | None = None, frequency: str | None = None) -> ExportSchedule:
        key = (installation_id, consumer_id, schedule_id)
        schedule = self._schedules.get(key)
        if not schedule:
            raise ValueError("Schedule not found")
        if enabled is not None:
            schedule.enabled = enabled
        if frequency is not None:
            if frequency not in VALID_FREQUENCIES:
                raise ValueError(f"Invalid frequency: {frequency}")
            schedule.frequency = frequency
        return schedule

    def mark_run(self, installation_id: str, consumer_id: str, schedule_id: str, now: datetime) -> ExportSchedule:
        key = (installation_id, consumer_id, schedule_id)
        schedule = self._schedules.get(key)
        if not schedule:
            raise ValueError("Schedule not found")
        schedule.last_run_at = now
        return schedule

    def list_schedules(self, installation_id: str, consumer_id: str, enabled_only: bool = False) -> list[ExportSchedule]:
        schedules = [s for (inst, cid, _), s in self._schedules.items() if inst == installation_id and cid == consumer_id]
        if enabled_only:
            schedules = [s for s in schedules if s.enabled]
        return sorted(schedules, key=lambda s: s.data_type)

    def delete(self, installation_id: str, consumer_id: str, schedule_id: str) -> None:
        key = (installation_id, consumer_id, schedule_id)
        if key not in self._schedules:
            raise ValueError("Schedule not found")
        del self._schedules[key]
