"""App API Developer API Migration Tracker — track API version migrations."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class MigrationTask:
    task_id: str
    consumer_id: str
    from_version: str
    to_version: str
    status: str = "pending"  # "pending", "in_progress", "completed", "failed"
    started_at: float | None = None
    completed_at: float | None = None
    notes: str = ""

class AppAPIDeveloperAPIApiMigrationTracker:
    def __init__(self) -> None:
        self._tasks: dict[tuple[str, str], MigrationTask] = {}

    def create(self, installation_id: str, task_id: str, consumer_id: str, from_version: str, to_version: str) -> MigrationTask:
        if not installation_id: raise ValueError("installation_id is required")
        if from_version == to_version: raise ValueError("from and to versions must differ")
        key = (installation_id, task_id)
        if key in self._tasks: raise ValueError(f"Task {task_id} exists")
        t = MigrationTask(task_id=task_id, consumer_id=consumer_id, from_version=from_version, to_version=to_version)
        self._tasks[key] = t
        return t

    def start(self, installation_id: str, task_id: str) -> MigrationTask:
        t = self._get(installation_id, task_id)
        t.status = "in_progress"
        t.started_at = time.time()
        return t

    def complete(self, installation_id: str, task_id: str, notes: str = "") -> MigrationTask:
        t = self._get(installation_id, task_id)
        t.status = "completed"
        t.completed_at = time.time()
        t.notes = notes
        return t

    def fail(self, installation_id: str, task_id: str, notes: str = "") -> MigrationTask:
        t = self._get(installation_id, task_id)
        t.status = "failed"
        t.notes = notes
        return t

    def progress(self, installation_id: str) -> dict[str, int]:
        tasks = [t for (inst, _), t in self._tasks.items() if inst == installation_id]
        return {s: sum(1 for t in tasks if t.status == s) for s in ("pending", "in_progress", "completed", "failed")}

    def pending(self, installation_id: str) -> list[MigrationTask]:
        return [t for (inst, _), t in self._tasks.items() if inst == installation_id and t.status in ("pending", "in_progress")]

    def _get(self, installation_id: str, task_id: str) -> MigrationTask:
        key = (installation_id, task_id)
        t = self._tasks.get(key)
        if t is None: raise KeyError(f"Task {task_id} not found")
        return t
