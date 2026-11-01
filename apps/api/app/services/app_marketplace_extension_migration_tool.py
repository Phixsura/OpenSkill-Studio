"""Extension Migration Tool — migrate extensions between platform versions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class MigrationStep:
    step_id: str
    name: str
    description: str
    status: str = "pending"  # pending, running, completed, failed, skipped
    duration_ms: float = 0.0
    error: str = ""


@dataclass
class Migration:
    migration_id: str
    extension_id: str
    from_version: str
    to_version: str
    steps: list[MigrationStep] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed, rolled_back
    started_at: float = 0.0
    completed_at: float = 0.0


class ExtMigrationToolService:
    def __init__(self):
        self._migrations: dict[str, Migration] = {}
        self._counter = 0

    def plan(self, extension_id: str, from_ver: str, to_ver: str,
             steps: list[tuple[str, str]]) -> Migration:
        self._counter += 1
        mid = f"mig-{self._counter}"
        migration_steps = [MigrationStep(step_id=f"s-{i+1}", name=n, description=d)
                           for i, (n, d) in enumerate(steps)]
        m = Migration(migration_id=mid, extension_id=extension_id,
                      from_version=from_ver, to_version=to_ver, steps=migration_steps)
        self._migrations[mid] = m
        return m

    def execute_step(self, migration_id: str, step_id: str,
                     success: bool = True, error: str = "") -> bool:
        m = self._migrations.get(migration_id)
        if not m or m.status in ("completed", "failed", "rolled_back"):
            return False
        if m.status == "pending":
            m.status = "running"
            m.started_at = time.time()
        for step in m.steps:
            if step.step_id == step_id:
                step.status = "completed" if success else "failed"
                step.error = error
                if not success:
                    m.status = "failed"
                # Check if all done
                if all(s.status == "completed" for s in m.steps):
                    m.status = "completed"
                    m.completed_at = time.time()
                return True
        return False

    def rollback(self, migration_id: str) -> bool:
        m = self._migrations.get(migration_id)
        if not m or m.status not in ("running", "failed"):
            return False
        m.status = "rolled_back"
        for step in m.steps:
            if step.status == "completed":
                step.status = "pending"  # mark as needing rollback
        return True

    def get_progress(self, migration_id: str) -> dict | None:
        m = self._migrations.get(migration_id)
        if not m: return None
        total = len(m.steps)
        done = sum(1 for s in m.steps if s.status == "completed")
        return {"status": m.status, "total": total, "completed": done,
                "percentage": round(done / total * 100) if total else 0}
