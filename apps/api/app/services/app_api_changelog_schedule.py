"""App API Changelog Schedule — schedule changelog publications."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import structlog

log = structlog.get_logger()

class PublishStatus(str, Enum):
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    CANCELLED = "cancelled"

@dataclass
class ScheduledChangelog:
    schedule_id: str
    version: str
    title: str
    publish_date: str
    status: PublishStatus = PublishStatus.SCHEDULED

class AppAPIChangelogSchedule:
    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str], ScheduledChangelog] = {}

    def schedule(self, installation_id: str, schedule_id: str, version: str, title: str, publish_date: str) -> ScheduledChangelog:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, schedule_id)
        if key in self._schedules: raise ValueError(f"Schedule {schedule_id} exists")
        s = ScheduledChangelog(schedule_id=schedule_id, version=version, title=title, publish_date=publish_date)
        self._schedules[key] = s
        return s

    def publish(self, installation_id: str, schedule_id: str) -> ScheduledChangelog:
        s = self._get(installation_id, schedule_id)
        s.status = PublishStatus.PUBLISHED
        return s

    def cancel(self, installation_id: str, schedule_id: str) -> ScheduledChangelog:
        s = self._get(installation_id, schedule_id)
        s.status = PublishStatus.CANCELLED
        return s

    def upcoming(self, installation_id: str) -> list[ScheduledChangelog]:
        return [s for (inst, _), s in self._schedules.items() if inst == installation_id and s.status == PublishStatus.SCHEDULED]

    def list_all(self, installation_id: str) -> list[ScheduledChangelog]:
        return [s for (inst, _), s in self._schedules.items() if inst == installation_id]

    def _get(self, installation_id: str, schedule_id: str) -> ScheduledChangelog:
        s = self._schedules.get((installation_id, schedule_id))
        if s is None: raise KeyError(f"Schedule {schedule_id} not found")
        return s
