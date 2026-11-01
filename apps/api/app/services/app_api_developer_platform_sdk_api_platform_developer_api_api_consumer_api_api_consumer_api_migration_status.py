"""API Consumer Migration Status — track consumer migration progress between versions."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class MigrationState(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"

@dataclass
class MigrationStatus:
    consumer_id: str
    from_version: str
    to_version: str
    state: MigrationState = MigrationState.NOT_STARTED
    progress_pct: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiMigrationStatus:
    def __init__(self) -> None:
        self._migrations: dict[tuple[str, str], MigrationStatus] = {}

    def start_migration(self, installation_id: str, consumer_id: str, from_version: str, to_version: str) -> MigrationStatus:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key in self._migrations and self._migrations[key].state == MigrationState.IN_PROGRESS:
            raise ValueError("Migration already in progress")
        ms = MigrationStatus(consumer_id=consumer_id, from_version=from_version, to_version=to_version, state=MigrationState.IN_PROGRESS, started_at=time.time())
        self._migrations[key] = ms
        return ms

    def update_progress(self, installation_id: str, consumer_id: str, progress_pct: float) -> MigrationStatus:
        ms = self._get(installation_id, consumer_id)
        ms.progress_pct = min(100.0, max(0.0, progress_pct))
        return ms

    def complete(self, installation_id: str, consumer_id: str) -> MigrationStatus:
        ms = self._get(installation_id, consumer_id)
        ms.state = MigrationState.COMPLETED
        ms.progress_pct = 100.0
        ms.completed_at = time.time()
        return ms

    def rollback(self, installation_id: str, consumer_id: str) -> MigrationStatus:
        ms = self._get(installation_id, consumer_id)
        ms.state = MigrationState.ROLLED_BACK
        return ms

    def in_progress(self, installation_id: str) -> list[MigrationStatus]:
        return [m for (inst, _), m in self._migrations.items() if inst == installation_id and m.state == MigrationState.IN_PROGRESS]

    def list_migrations(self, installation_id: str) -> list[MigrationStatus]:
        return [m for (inst, _), m in self._migrations.items() if inst == installation_id]

    def _get(self, installation_id: str, consumer_id: str) -> MigrationStatus:
        ms = self._migrations.get((installation_id, consumer_id))
        if ms is None: raise KeyError(f"No migration for {consumer_id}")
        return ms
