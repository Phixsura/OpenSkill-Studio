"""App API Developer API Migration Status — track consumer migration progress."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerMigration:
    consumer_id: str
    from_version: str
    to_version: str
    migrated: bool = False
    last_old_version_call: str = ""

class AppAPIDeveloperAPIMigrationStatus:
    def __init__(self) -> None:
        self._migrations: dict[tuple[str, str], ConsumerMigration] = {}

    def track(self, installation_id: str, consumer_id: str, from_version: str, to_version: str) -> ConsumerMigration:
        if not installation_id: raise ValueError("installation_id is required")
        m = ConsumerMigration(consumer_id=consumer_id, from_version=from_version, to_version=to_version)
        self._migrations[(installation_id, consumer_id)] = m
        return m

    def mark_migrated(self, installation_id: str, consumer_id: str) -> ConsumerMigration:
        m = self._migrations.get((installation_id, consumer_id))
        if m is None: raise KeyError(f"No migration for {consumer_id}")
        m.migrated = True
        return m

    def migration_progress(self, installation_id: str) -> dict:
        all_m = [m for (inst, _), m in self._migrations.items() if inst == installation_id]
        if not all_m: return {"total": 0, "migrated": 0, "pct": 100.0}
        migrated = sum(1 for m in all_m if m.migrated)
        return {"total": len(all_m), "migrated": migrated, "pct": round(migrated / len(all_m) * 100, 1)}

    def not_migrated(self, installation_id: str) -> list[ConsumerMigration]:
        return [m for (inst, _), m in self._migrations.items() if inst == installation_id and not m.migrated]

    def list_all(self, installation_id: str) -> list[ConsumerMigration]:
        return [m for (inst, _), m in self._migrations.items() if inst == installation_id]
