"""Consumer API Endpoint Migration Tracker — track consumer progress on endpoint migrations."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class MigrationTarget:
    old_endpoint: str
    new_endpoint: str
    deadline: datetime
    status: str = "pending"  # "pending", "in_progress", "completed", "overdue"

@dataclass
class ConsumerMigration:
    consumer_id: str
    migrations: list[MigrationTarget] = field(default_factory=list)
    completed_count: int = 0
    total_count: int = 0
    progress_pct: float = 0.0

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointMigrationTracker:
    def __init__(self) -> None:
        self._migrations: dict[tuple[str, str, str], MigrationTarget] = {}  # (inst, consumer, old_ep)

    def add_migration(self, installation_id: str, consumer_id: str, target: MigrationTarget) -> MigrationTarget:
        if not installation_id:
            raise ValueError("installation_id is required")
        if target.old_endpoint == target.new_endpoint:
            raise ValueError("Old and new endpoints must differ")
        self._migrations[(installation_id, consumer_id, target.old_endpoint)] = target
        return target

    def mark_completed(self, installation_id: str, consumer_id: str, old_endpoint: str) -> MigrationTarget:
        key = (installation_id, consumer_id, old_endpoint)
        target = self._migrations.get(key)
        if not target:
            raise ValueError("Migration not found")
        target.status = "completed"
        return target

    def check_overdue(self, installation_id: str, consumer_id: str, now: datetime) -> list[MigrationTarget]:
        overdue = []
        for (inst, cid, _), t in self._migrations.items():
            if inst == installation_id and cid == consumer_id and t.status == "pending" and now > t.deadline:
                t.status = "overdue"
                overdue.append(t)
        return overdue

    def get_progress(self, installation_id: str, consumer_id: str) -> ConsumerMigration:
        targets = [t for (inst, cid, _), t in self._migrations.items() if inst == installation_id and cid == consumer_id]
        completed = sum(1 for t in targets if t.status == "completed")
        total = len(targets)
        pct = round(completed / total * 100, 1) if total > 0 else 0
        return ConsumerMigration(consumer_id=consumer_id, migrations=sorted(targets, key=lambda t: t.deadline), completed_count=completed, total_count=total, progress_pct=pct)

    def list_all_migrations(self, installation_id: str) -> list[MigrationTarget]:
        return [t for (inst, _, _), t in self._migrations.items() if inst == installation_id]
