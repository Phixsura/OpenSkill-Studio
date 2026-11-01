"""Data Migration — versioned data migrations for extension config/storage.

When extensions release new versions, their data schemas may change.
This service manages forward/rollback migrations with version tracking.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class MigrationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Migration:
    migration_id: str
    extension_id: str
    from_version: str
    to_version: str
    description: str
    up_fn: str  # simulated: name of forward migration function
    down_fn: str  # simulated: name of rollback function
    status: MigrationStatus = MigrationStatus.PENDING
    applied_at: str = ""
    error: str = ""


class DataMigrationService:
    """Manages versioned data migrations for extensions."""

    def __init__(self):
        self._migrations: dict[str, Migration] = {}
        self._applied: dict[str, list[str]] = {}  # ext_id -> [migration_ids in order]

    def register(self, migration: Migration) -> Migration:
        """Register a new migration."""
        self._migrations[migration.migration_id] = migration
        return migration

    def get_pending(self, extension_id: str) -> list[Migration]:
        """Get pending migrations for an extension in order."""
        applied = set(self._applied.get(extension_id, []))
        return [
            m for m in self._migrations.values()
            if m.extension_id == extension_id
            and m.migration_id not in applied
            and m.status == MigrationStatus.PENDING
        ]

    def apply(self, migration_id: str) -> tuple[bool, str]:
        """Apply a forward migration."""
        m = self._migrations.get(migration_id)
        if not m:
            return False, "Migration not found"
        if m.status != MigrationStatus.PENDING:
            return False, f"Migration is {m.status.value}, not pending"

        m.status = MigrationStatus.RUNNING
        try:
            # Simulate migration execution
            m.status = MigrationStatus.COMPLETED
            m.applied_at = datetime.now(timezone.utc).isoformat()
            self._applied.setdefault(m.extension_id, []).append(m.migration_id)
            return True, f"Migrated {m.from_version} -> {m.to_version}"
        except Exception as e:
            m.status = MigrationStatus.FAILED
            m.error = str(e)
            return False, str(e)

    def rollback(self, migration_id: str) -> tuple[bool, str]:
        """Rollback an applied migration."""
        m = self._migrations.get(migration_id)
        if not m:
            return False, "Migration not found"
        if m.status != MigrationStatus.COMPLETED:
            return False, "Can only rollback completed migrations"

        applied = self._applied.get(m.extension_id, [])
        if applied and applied[-1] != migration_id:
            return False, "Can only rollback the most recent migration"

        m.status = MigrationStatus.ROLLED_BACK
        applied.pop()
        return True, f"Rolled back {m.to_version} -> {m.from_version}"

    def get_history(self, extension_id: str) -> list[Migration]:
        """Get migration history for an extension."""
        return [
            self._migrations[mid]
            for mid in self._applied.get(extension_id, [])
            if mid in self._migrations
        ]

    def get_current_version(self, extension_id: str) -> str:
        """Get the current data version after all applied migrations."""
        applied_ids = self._applied.get(extension_id, [])
        if not applied_ids:
            return "0.0.0"
        last = self._migrations.get(applied_ids[-1])
        return last.to_version if last else "0.0.0"
