"""Consumer API Key Rotation Schedule — schedule automatic key rotations."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class RotationSchedule:
    schedule_id: str
    consumer_id: str
    key_id: str
    interval_days: int = 90
    last_rotated_at: datetime | None = None
    next_rotation_at: datetime | None = None
    auto_rotate: bool = True
    notify_days_before: int = 7

@dataclass
class RotationCheck:
    key_id: str
    due: bool
    days_until: int
    overdue: bool
    notify: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyRotationSchedule:
    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str, str], RotationSchedule] = {}  # (inst, consumer, key)

    def set_schedule(self, installation_id: str, schedule: RotationSchedule) -> RotationSchedule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if schedule.interval_days < 1:
            raise ValueError("interval_days must be positive")
        if schedule.last_rotated_at:
            schedule.next_rotation_at = schedule.last_rotated_at + timedelta(days=schedule.interval_days)
        key = (installation_id, schedule.consumer_id, schedule.key_id)
        self._schedules[key] = schedule
        return schedule

    def check(self, installation_id: str, consumer_id: str, key_id: str, now: datetime) -> RotationCheck:
        key = (installation_id, consumer_id, key_id)
        schedule = self._schedules.get(key)
        if not schedule or not schedule.next_rotation_at:
            return RotationCheck(key_id=key_id, due=False, days_until=999, overdue=False, notify=False)
        delta = (schedule.next_rotation_at - now).days
        due = delta <= 0
        overdue = delta < -schedule.notify_days_before
        notify = delta <= schedule.notify_days_before
        return RotationCheck(key_id=key_id, due=due, days_until=max(0, delta), overdue=overdue, notify=notify)

    def mark_rotated(self, installation_id: str, consumer_id: str, key_id: str, now: datetime) -> RotationSchedule:
        key = (installation_id, consumer_id, key_id)
        schedule = self._schedules.get(key)
        if not schedule:
            raise ValueError("Schedule not found")
        schedule.last_rotated_at = now
        schedule.next_rotation_at = now + timedelta(days=schedule.interval_days)
        return schedule

    def list_due(self, installation_id: str, now: datetime) -> list[RotationCheck]:
        results = []
        for (inst, cid, kid), s in self._schedules.items():
            if inst != installation_id:
                continue
            check = self.check(installation_id, cid, kid, now)
            if check.due or check.notify:
                results.append(check)
        return sorted(results, key=lambda c: c.days_until)

    def list_schedules(self, installation_id: str, consumer_id: str) -> list[RotationSchedule]:
        return [s for (inst, cid, _), s in self._schedules.items() if inst == installation_id and cid == consumer_id]
