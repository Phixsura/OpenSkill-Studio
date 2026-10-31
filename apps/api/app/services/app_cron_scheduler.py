"""App Cron Scheduler — scheduled task management for installed apps.

Manages recurring scheduled tasks:
- Register tasks with cron-like schedules
- Enable/disable tasks
- Execution history tracking
- Next-run computation
- Per-installation scoped tasks
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class TaskStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    RUNNING = "running"


@dataclass
class ScheduledTask:
    """A scheduled recurring task."""

    task_id: str
    installation_id: str
    name: str
    schedule: str  # human-readable, e.g. "every 5 minutes", "daily at 3am"
    interval_seconds: int  # computed interval
    status: TaskStatus = TaskStatus.ENABLED
    last_run_at: float | None = None
    next_run_at: float | None = None
    run_count: int = 0
    last_error: str | None = None
    created_at: float = field(default_factory=time.time)


@dataclass
class RunRecord:
    """Record of a task execution."""

    task_id: str
    started_at: float
    completed_at: float | None = None
    success: bool = True
    duration_ms: float = 0.0
    error: str | None = None


class AppCronScheduler:
    """Scheduled task management for installed apps."""

    def __init__(self) -> None:
        self._tasks: dict[tuple[str, str], ScheduledTask] = {}
        self._runs: dict[tuple[str, str], list[RunRecord]] = {}

    def register_task(
        self,
        installation_id: str,
        task_id: str,
        name: str,
        schedule: str,
        interval_seconds: int,
        now: float | None = None,
    ) -> ScheduledTask:
        """Register a new scheduled task."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not task_id:
            raise ValueError("task_id is required")
        if not name:
            raise ValueError("name is required")
        if interval_seconds < 1:
            raise ValueError("interval_seconds must be >= 1")

        key = (installation_id, task_id)
        if key in self._tasks:
            raise ValueError(f"Task {task_id} already exists")

        now = now or time.time()
        task = ScheduledTask(
            task_id=task_id,
            installation_id=installation_id,
            name=name,
            schedule=schedule,
            interval_seconds=interval_seconds,
            next_run_at=now + interval_seconds,
            created_at=now,
        )
        self._tasks[key] = task
        return task

    def record_run(
        self,
        installation_id: str,
        task_id: str,
        success: bool = True,
        duration_ms: float = 0.0,
        error: str = "",
        now: float | None = None,
    ) -> RunRecord:
        """Record a task execution."""
        task = self._get(installation_id, task_id)
        now = now or time.time()

        record = RunRecord(
            task_id=task_id,
            started_at=now - (duration_ms / 1000),
            completed_at=now,
            success=success,
            duration_ms=max(0, duration_ms),
            error=error or None,
        )

        key = (installation_id, task_id)
        self._runs.setdefault(key, []).append(record)

        task.last_run_at = now
        task.next_run_at = now + task.interval_seconds
        task.run_count += 1
        task.last_error = error if not success else None

        return record

    def enable_task(self, installation_id: str, task_id: str) -> ScheduledTask:
        task = self._get(installation_id, task_id)
        task.status = TaskStatus.ENABLED
        return task

    def disable_task(self, installation_id: str, task_id: str) -> ScheduledTask:
        task = self._get(installation_id, task_id)
        task.status = TaskStatus.DISABLED
        return task

    def get_task(self, installation_id: str, task_id: str) -> ScheduledTask:
        return self._get(installation_id, task_id)

    def list_tasks(self, installation_id: str) -> list[ScheduledTask]:
        return [
            t for (inst, _), t in self._tasks.items()
            if inst == installation_id
        ]

    def get_due_tasks(self, installation_id: str, now: float | None = None) -> list[ScheduledTask]:
        """Get tasks that are due to run."""
        now = now or time.time()
        return [
            t for (inst, _), t in self._tasks.items()
            if inst == installation_id
            and t.status == TaskStatus.ENABLED
            and t.next_run_at is not None
            and now >= t.next_run_at
        ]

    def get_run_history(
        self, installation_id: str, task_id: str, limit: int = 20
    ) -> list[RunRecord]:
        key = (installation_id, task_id)
        runs = self._runs.get(key, [])
        return list(reversed(runs[-limit:]))

    def _get(self, installation_id: str, task_id: str) -> ScheduledTask:
        key = (installation_id, task_id)
        task = self._tasks.get(key)
        if task is None:
            raise KeyError(f"Task {task_id} not found")
        return task
