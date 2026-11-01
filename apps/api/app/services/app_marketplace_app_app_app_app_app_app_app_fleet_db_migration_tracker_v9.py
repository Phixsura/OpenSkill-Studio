"""Fleet DB Migration Tracker v9 — track schema migration across envs."""
from __future__ import annotations
def fleet_db_migration_tracker_v9(envs: list[dict]) -> dict:
    synced = [e for e in envs if e.get("migration_synced")]
    pending = sum(e.get("pending_migrations", 0) for e in envs)
    total_applied = sum(e.get("applied", 0) for e in envs)
    return {"environments": len(envs), "synced": len(synced), "pending_migrations": pending,
            "total_applied": total_applied, "healthy": pending == 0}
