"""App Migration Tracker — track database/schema migration status.

Manages migration lifecycle:
- Register migrations with dependencies
- Track execution status (pending/running/completed/failed)
- Detect out-of-order migrations
- Per-installation scoped migrations
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class MigrationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Migration:
    """A database migration."""

    migration_id: str
    version: str
    description: str
    status: MigrationStatus = MigrationStatus.PENDING
    depends_on: str | None = None
    started_at: float | None = None
    completed_at: float | None = None
    error: str = ""

    @property
    def duration_ms(self) -> float | None:
        if self.started_at and self.completed_at:
            return round((self.completed_at - self.started_at) * 1000, 1)
        return None


class AppMigrationTracker:
    """Track database/schema migration status."""

    def __init__(self) -> None:
        self._migrations: dict[tuple[str, str], Migration] = {}

    def register(
        self, installation_id: str, migration_id: str, version: str,
        description: str, depends_on: str | None = None,
    ) -> Migration:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not migration_id:
            raise ValueError("migration_id is required")

        key = (installation_id, migration_id)
        if key in self._migrations:
            raise ValueError(f"Migration {migration_id} already registered")

        m = Migration(
            migration_id=migration_id, version=version,
            description=description, depends_on=depends_on,
        )
        self._migrations[key] = m
        return m

    def start(self, installation_id: str, migration_id: str) -> Migration:
        m = self._get(installation_id, migration_id)
        if m.status != MigrationStatus.PENDING:
            raise ValueError(f"Migration {migration_id} is not pending")

        # Check dependency
        if m.depends_on:
            dep = self._migrations.get((installation_id, m.depends_on))
            if dep is None or dep.status != MigrationStatus.COMPLETED:
                raise ValueError(f"Dependency {m.depends_on} not completed")

        m.status = MigrationStatus.RUNNING
        m.started_at = time.time()
        return m

    def complete(self, installation_id: str, migration_id: str) -> Migration:
        m = self._get(installation_id, migration_id)
        if m.status != MigrationStatus.RUNNING:
            raise ValueError("Migration not running")
        m.status = MigrationStatus.COMPLETED
        m.completed_at = time.time()
        return m

    def fail(self, installation_id: str, migration_id: str, error: str = "") -> Migration:
        m = self._get(installation_id, migration_id)
        if m.status != MigrationStatus.RUNNING:
            raise ValueError("Migration not running")
        m.status = MigrationStatus.FAILED
        m.completed_at = time.time()
        m.error = error
        return m

    def rollback(self, installation_id: str, migration_id: str) -> Migration:
        m = self._get(installation_id, migration_id)
        if m.status not in (MigrationStatus.COMPLETED, MigrationStatus.FAILED):
            raise ValueError("Can only rollback completed or failed migrations")
        m.status = MigrationStatus.ROLLED_BACK
        return m

    def pending(self, installation_id: str) -> list[Migration]:
        return [
            m for (inst, _), m in self._migrations.items()
            if inst == installation_id and m.status == MigrationStatus.PENDING
        ]

    def list_all(self, installation_id: str) -> list[Migration]:
        return [m for (inst, _), m in self._migrations.items() if inst == installation_id]

    def _get(self, installation_id: str, migration_id: str) -> Migration:
        key = (installation_id, migration_id)
        m = self._migrations.get(key)
        if m is None:
            raise KeyError(f"Migration {migration_id} not found")
        return m
