"""App Task Queue — manage background task execution.

Manages task queues:
- Enqueue tasks with priority
- Dequeue and process in priority order
- Track task status (pending/running/completed/failed)
- Retry failed tasks
- Per-installation scoped queues
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueueTask:
    """A task in the queue."""

    task_id: str
    task_type: str
    payload: dict
    priority: int = 0  # higher = more urgent
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    max_retries: int = 3
    error: str = ""
    created_at: float = field(default_factory=time.time)


class AppTaskQueue:
    """Manage background task execution."""

    def __init__(self) -> None:
        self._queues: dict[str, list[QueueTask]] = {}

    def enqueue(
        self, installation_id: str, task_id: str, task_type: str,
        payload: dict, priority: int = 0, max_retries: int = 3,
    ) -> QueueTask:
        if not installation_id:
            raise ValueError("installation_id is required")

        task = QueueTask(
            task_id=task_id, task_type=task_type, payload=payload,
            priority=priority, max_retries=max_retries,
        )
        self._queues.setdefault(installation_id, []).append(task)
        return task

    def dequeue(self, installation_id: str) -> QueueTask | None:
        """Get next pending task by priority (highest first)."""
        tasks = self._queues.get(installation_id, [])
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        if not pending:
            return None
        pending.sort(key=lambda t: t.priority, reverse=True)
        task = pending[0]
        task.status = TaskStatus.RUNNING
        task.attempts += 1
        return task

    def complete(self, installation_id: str, task_id: str) -> QueueTask:
        t = self._find(installation_id, task_id)
        if t.status != TaskStatus.RUNNING:
            raise ValueError("Task not running")
        t.status = TaskStatus.COMPLETED
        return t

    def fail(self, installation_id: str, task_id: str, error: str = "") -> QueueTask:
        t = self._find(installation_id, task_id)
        if t.status != TaskStatus.RUNNING:
            raise ValueError("Task not running")
        t.error = error
        if t.attempts < t.max_retries:
            t.status = TaskStatus.PENDING  # retry
        else:
            t.status = TaskStatus.FAILED
        return t

    def pending_count(self, installation_id: str) -> int:
        return sum(1 for t in self._queues.get(installation_id, []) if t.status == TaskStatus.PENDING)

    def stats(self, installation_id: str) -> dict[str, int]:
        tasks = self._queues.get(installation_id, [])
        return {
            "pending": sum(1 for t in tasks if t.status == TaskStatus.PENDING),
            "running": sum(1 for t in tasks if t.status == TaskStatus.RUNNING),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in tasks if t.status == TaskStatus.FAILED),
        }

    def list_tasks(self, installation_id: str, status: TaskStatus | None = None) -> list[QueueTask]:
        tasks = self._queues.get(installation_id, [])
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def _find(self, installation_id: str, task_id: str) -> QueueTask:
        for t in self._queues.get(installation_id, []):
            if t.task_id == task_id:
                return t
        raise KeyError(f"Task {task_id} not found")
