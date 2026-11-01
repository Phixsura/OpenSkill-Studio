"""Sandbox Task Queue — async task queue for extension background jobs.

Manages a priority task queue with workers, retry on failure, task
dependencies, progress tracking, and result storage.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"  # waiting on dependency


@dataclass
class QueueTask:
    task_id: str
    sandbox_id: str
    name: str
    payload: dict = field(default_factory=dict)
    priority: int = 0
    state: TaskState = TaskState.PENDING
    progress: int = 0  # 0-100
    result: dict | None = None
    error: str = ""
    depends_on: str = ""  # task_id of dependency
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class SandboxTaskQueueService:
    """Manages async task queue for extension background processing."""

    MAX_PENDING = 1000

    def __init__(self):
        self._tasks: dict[str, QueueTask] = {}
        self._by_sandbox: dict[str, list[str]] = defaultdict(list)

    def enqueue(self, sandbox_id: str, name: str, payload: dict | None = None,
                priority: int = 0, depends_on: str = "",
                max_retries: int = 3) -> QueueTask | dict:
        pending = sum(1 for tid in self._by_sandbox.get(sandbox_id, [])
                      if self._tasks.get(tid, QueueTask("", "", "")).state in
                      (TaskState.PENDING, TaskState.WAITING))
        if pending >= self.MAX_PENDING:
            return {"error": "Queue full"}

        task_id = f"task_{secrets.token_urlsafe(8)}"
        state = TaskState.PENDING
        if depends_on:
            dep = self._tasks.get(depends_on)
            if dep and dep.state != TaskState.COMPLETED:
                state = TaskState.WAITING

        task = QueueTask(
            task_id=task_id, sandbox_id=sandbox_id, name=name,
            payload=payload or {}, priority=priority, state=state,
            depends_on=depends_on, max_retries=max_retries,
        )
        self._tasks[task_id] = task
        self._by_sandbox[sandbox_id].append(task_id)
        return task

    def dequeue(self, sandbox_id: str) -> QueueTask | None:
        """Get highest priority pending task."""
        pending = [self._tasks[tid] for tid in self._by_sandbox.get(sandbox_id, [])
                   if self._tasks[tid].state == TaskState.PENDING]
        if not pending:
            return None
        pending.sort(key=lambda t: t.priority, reverse=True)
        task = pending[0]
        task.state = TaskState.RUNNING
        task.started_at = time.time()
        return task

    def complete(self, task_id: str, result: dict | None = None) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.state != TaskState.RUNNING:
            return False
        task.state = TaskState.COMPLETED
        task.result = result
        task.progress = 100
        task.completed_at = time.time()
        # Unblock dependents
        for t in self._tasks.values():
            if t.depends_on == task_id and t.state == TaskState.WAITING:
                t.state = TaskState.PENDING
        return True

    def fail(self, task_id: str, error: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.state != TaskState.RUNNING:
            return False
        task.retry_count += 1
        if task.retry_count < task.max_retries:
            task.state = TaskState.PENDING
            task.error = error
        else:
            task.state = TaskState.FAILED
            task.error = error
            task.completed_at = time.time()
        return True

    def update_progress(self, task_id: str, progress: int) -> bool:
        task = self._tasks.get(task_id)
        if task and task.state == TaskState.RUNNING:
            task.progress = max(0, min(100, progress))
            return True
        return False

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.state in (TaskState.PENDING, TaskState.WAITING):
            task.state = TaskState.CANCELLED
            return True
        return False

    def get_stats(self, sandbox_id: str) -> dict:
        tasks = [self._tasks[tid] for tid in self._by_sandbox.get(sandbox_id, [])]
        by_state: dict[str, int] = defaultdict(int)
        for t in tasks:
            by_state[t.state.value] += 1
        return {"total": len(tasks), "by_state": dict(by_state)}
