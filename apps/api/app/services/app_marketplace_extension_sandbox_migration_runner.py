"""Sandbox Migration Runner — run data migrations for extension upgrades.

Executes versioned migrations with up/down support, checkpoint tracking,
rollback on failure, and migration history.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class MigrationState(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Migration:
    migration_id: str
    version: str
    name: str
    up_action: str
    down_action: str
    state: MigrationState = MigrationState.PENDING
    applied_at: float = 0.0
    duration_ms: float = 0.0
    error: str = ""


class SandboxMigrationRunnerService:
    """Runs versioned migrations with rollback support."""

    def __init__(self):
        self._migrations: dict[str, list[Migration]] = {}

    def register(self, sandbox_id: str, version: str, name: str,
                 up_action: str, down_action: str) -> Migration:
        migrations = self._migrations.setdefault(sandbox_id, [])
        # Check duplicate version
        if any(m.version == version for m in migrations):
            raise ValueError(f"Migration {version} already registered")
        m = Migration(
            migration_id=f"mig_{secrets.token_urlsafe(6)}",
            version=version, name=name,
            up_action=up_action, down_action=down_action,
        )
        migrations.append(m)
        migrations.sort(key=lambda x: x.version)
        return m

    def migrate_up(self, sandbox_id: str) -> list[Migration]:
        migrations = self._migrations.get(sandbox_id, [])
        applied: list[Migration] = []
        for m in migrations:
            if m.state != MigrationState.PENDING:
                continue
            start = time.time()
            # Simulate execution
            m.state = MigrationState.APPLIED
            m.applied_at = time.time()
            m.duration_ms = round((time.time() - start) * 1000, 1)
            applied.append(m)
        return applied

    def migrate_up_to(self, sandbox_id: str, target_version: str) -> list[Migration]:
        migrations = self._migrations.get(sandbox_id, [])
        applied: list[Migration] = []
        for m in migrations:
            if m.version > target_version:
                break
            if m.state != MigrationState.PENDING:
                continue
            m.state = MigrationState.APPLIED
            m.applied_at = time.time()
            applied.append(m)
        return applied

    def rollback_last(self, sandbox_id: str) -> Migration | None:
        migrations = self._migrations.get(sandbox_id, [])
        applied = [m for m in migrations if m.state == MigrationState.APPLIED]
        if not applied:
            return None
        last = applied[-1]
        last.state = MigrationState.ROLLED_BACK
        return last

    def rollback_to(self, sandbox_id: str, target_version: str) -> list[Migration]:
        migrations = self._migrations.get(sandbox_id, [])
        rolled_back: list[Migration] = []
        for m in reversed(migrations):
            if m.version <= target_version:
                break
            if m.state == MigrationState.APPLIED:
                m.state = MigrationState.ROLLED_BACK
                rolled_back.append(m)
        return rolled_back

    def fail_migration(self, sandbox_id: str, version: str, error: str) -> bool:
        migrations = self._migrations.get(sandbox_id, [])
        for m in migrations:
            if m.version == version:
                m.state = MigrationState.FAILED
                m.error = error
                return True
        return False

    def get_status(self, sandbox_id: str) -> dict:
        migrations = self._migrations.get(sandbox_id, [])
        return {
            "total": len(migrations),
            "applied": sum(1 for m in migrations if m.state == MigrationState.APPLIED),
            "pending": sum(1 for m in migrations if m.state == MigrationState.PENDING),
            "failed": sum(1 for m in migrations if m.state == MigrationState.FAILED),
            "current_version": next((m.version for m in reversed(migrations)
                                     if m.state == MigrationState.APPLIED), None),
        }

    def list_migrations(self, sandbox_id: str) -> list[Migration]:
        return list(self._migrations.get(sandbox_id, []))
