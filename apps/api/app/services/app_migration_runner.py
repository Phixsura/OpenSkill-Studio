"""App Migration Runner — manage schema/data migrations for installed apps.

Tracks migration lifecycle for installed apps:
- Register migrations with version ordering
- Track applied/pending/failed status
- Execute migrations in order with rollback tracking
- Per-installation migration history
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
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Migration:
    """A single migration record."""

    migration_id: str
    version: int  # sequential order
    description: str
    status: MigrationStatus = MigrationStatus.PENDING
    applied_at: float | None = None
    duration_ms: float | None = None
    error: str | None = None


class AppMigrationRunner:
    """Manage schema/data migrations for installed apps."""

    def __init__(self) -> None:
        # (installation_id, migration_id) → Migration
        self._migrations: dict[tuple[str, str], Migration] = {}
        # installation_id → ordered list of migration_ids
        self._order: dict[str, list[str]] = {}

    def register_migration(
        self,
        installation_id: str,
        migration_id: str,
        version: int,
        description: str,
    ) -> Migration:
        """Register a new migration."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not migration_id:
            raise ValueError("migration_id is required")
        if version < 1:
            raise ValueError("version must be >= 1")
        if not description:
            raise ValueError("description is required")

        key = (installation_id, migration_id)
        if key in self._migrations:
            raise ValueError(f"Migration {migration_id} already registered")

        # Check version uniqueness
        for (inst, _), m in self._migrations.items():
            if inst == installation_id and m.version == version:
                raise ValueError(f"Version {version} already used by {m.migration_id}")

        migration = Migration(
            migration_id=migration_id,
            version=version,
            description=description,
        )
        self._migrations[key] = migration

        order = self._order.setdefault(installation_id, [])
        order.append(migration_id)
        order.sort(key=lambda mid: self._migrations[(installation_id, mid)].version)

        return migration

    def apply_migration(
        self,
        installation_id: str,
        migration_id: str,
        duration_ms: float = 0.0,
        now: float | None = None,
    ) -> Migration:
        """Mark a migration as applied."""
        m = self._get(installation_id, migration_id)
        if m.status not in (MigrationStatus.PENDING, MigrationStatus.FAILED):
            raise ValueError(f"Cannot apply migration in {m.status} state")

        # Ensure all previous migrations are applied
        order = self._order.get(installation_id, [])
        for mid in order:
            if mid == migration_id:
                break
            prev = self._migrations[(installation_id, mid)]
            if prev.status != MigrationStatus.APPLIED:
                raise ValueError(f"Previous migration {mid} not applied")

        m.status = MigrationStatus.APPLIED
        m.applied_at = now or time.time()
        m.duration_ms = max(0.0, duration_ms)
        m.error = None
        return m

    def fail_migration(
        self, installation_id: str, migration_id: str, error: str = ""
    ) -> Migration:
        """Mark a migration as failed."""
        m = self._get(installation_id, migration_id)
        if m.status not in (MigrationStatus.PENDING, MigrationStatus.RUNNING):
            raise ValueError(f"Cannot fail migration in {m.status} state")
        m.status = MigrationStatus.FAILED
        m.error = error
        return m

    def rollback_migration(
        self, installation_id: str, migration_id: str
    ) -> Migration:
        """Roll back an applied migration."""
        m = self._get(installation_id, migration_id)
        if m.status != MigrationStatus.APPLIED:
            raise ValueError(f"Cannot roll back migration in {m.status} state")

        # Ensure no later migrations are applied
        order = self._order.get(installation_id, [])
        found = False
        for mid in order:
            if mid == migration_id:
                found = True
                continue
            if found:
                later = self._migrations[(installation_id, mid)]
                if later.status == MigrationStatus.APPLIED:
                    raise ValueError(f"Later migration {mid} still applied")

        m.status = MigrationStatus.ROLLED_BACK
        m.applied_at = None
        return m

    def get_migration(self, installation_id: str, migration_id: str) -> Migration:
        return self._get(installation_id, migration_id)

    def list_migrations(self, installation_id: str) -> list[Migration]:
        """List all migrations in version order."""
        order = self._order.get(installation_id, [])
        return [self._migrations[(installation_id, mid)] for mid in order]

    def get_pending(self, installation_id: str) -> list[Migration]:
        """Get pending migrations in order."""
        return [
            m for m in self.list_migrations(installation_id)
            if m.status in (MigrationStatus.PENDING, MigrationStatus.FAILED)
        ]

    def current_version(self, installation_id: str) -> int:
        """Get the highest applied migration version."""
        applied = [
            m.version for m in self.list_migrations(installation_id)
            if m.status == MigrationStatus.APPLIED
        ]
        return max(applied) if applied else 0

    def _get(self, installation_id: str, migration_id: str) -> Migration:
        key = (installation_id, migration_id)
        m = self._migrations.get(key)
        if m is None:
            raise KeyError(f"Migration {migration_id} not found")
        return m
