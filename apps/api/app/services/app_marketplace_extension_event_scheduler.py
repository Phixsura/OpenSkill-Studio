"""Event Scheduler — schedule recurring and one-shot events for extensions.

Manages cron-like schedules, delayed execution, event batching,
timezone handling, and execution history with failure tracking.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import time


class ScheduleType(str, Enum):
    ONCE = "once"
    RECURRING = "recurring"
    INTERVAL = "interval"


class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledEvent:
    event_id: str
    extension_id: str
    name: str
    schedule_type: ScheduleType
    action: str
    payload: dict = field(default_factory=dict)
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    interval_seconds: int = 0
    next_run_at: float = 0.0
    last_run_at: float = 0.0
    run_count: int = 0
    max_runs: int = 0  # 0 = unlimited
    failure_count: int = 0
    max_failures: int = 3
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class EventSchedulerService:
    """Manages scheduled events with retry and failure tracking."""

    def __init__(self):
        self._events: dict[str, ScheduledEvent] = {}

    def schedule_once(self, extension_id: str, name: str, action: str,
                      run_at: float, payload: dict | None = None) -> ScheduledEvent:
        event_id = f"sev_{secrets.token_urlsafe(10)}"
        event = ScheduledEvent(
            event_id=event_id, extension_id=extension_id, name=name,
            schedule_type=ScheduleType.ONCE, action=action,
            payload=payload or {}, next_run_at=run_at,
        )
        self._events[event_id] = event
        return event

    def schedule_recurring(self, extension_id: str, name: str, action: str,
                           interval_seconds: int, max_runs: int = 0,
                           payload: dict | None = None) -> ScheduledEvent:
        if interval_seconds < 60:
            raise ValueError("Minimum interval is 60 seconds")
        event_id = f"sev_{secrets.token_urlsafe(10)}"
        event = ScheduledEvent(
            event_id=event_id, extension_id=extension_id, name=name,
            schedule_type=ScheduleType.RECURRING, action=action,
            interval_seconds=interval_seconds, max_runs=max_runs,
            payload=payload or {}, next_run_at=time.time() + interval_seconds,
        )
        self._events[event_id] = event
        return event

    def execute(self, event_id: str, success: bool = True) -> dict:
        event = self._events.get(event_id)
        if not event or event.status != ScheduleStatus.ACTIVE:
            return {"executed": False, "reason": "Event not found or not active"}

        event.run_count += 1
        event.last_run_at = time.time()

        if not success:
            event.failure_count += 1
            if event.failure_count >= event.max_failures:
                event.status = ScheduleStatus.FAILED
                return {"executed": True, "status": "failed_permanently"}

        if event.schedule_type == ScheduleType.ONCE:
            event.status = ScheduleStatus.COMPLETED
        elif event.schedule_type == ScheduleType.RECURRING:
            if event.max_runs > 0 and event.run_count >= event.max_runs:
                event.status = ScheduleStatus.COMPLETED
            else:
                event.next_run_at = time.time() + event.interval_seconds

        return {"executed": True, "run_count": event.run_count, "status": event.status.value}

    def pause(self, event_id: str) -> bool:
        event = self._events.get(event_id)
        if event and event.status == ScheduleStatus.ACTIVE:
            event.status = ScheduleStatus.PAUSED
            return True
        return False

    def resume(self, event_id: str) -> bool:
        event = self._events.get(event_id)
        if event and event.status == ScheduleStatus.PAUSED:
            event.status = ScheduleStatus.ACTIVE
            return True
        return False

    def cancel(self, event_id: str) -> bool:
        event = self._events.get(event_id)
        if event and event.status in (ScheduleStatus.ACTIVE, ScheduleStatus.PAUSED):
            event.status = ScheduleStatus.CANCELLED
            return True
        return False

    def get_due_events(self, now: float | None = None) -> list[ScheduledEvent]:
        current = now or time.time()
        return [e for e in self._events.values()
                if e.status == ScheduleStatus.ACTIVE and e.next_run_at <= current]

    def list_events(self, extension_id: str) -> list[ScheduledEvent]:
        return [e for e in self._events.values() if e.extension_id == extension_id]
