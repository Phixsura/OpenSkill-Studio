"""Fleet API Migration Guide v9 — track API migration progress."""
from __future__ import annotations
def fleet_api_migration_guide_v9(migrations: list[dict]) -> dict:
    completed = [m for m in migrations if m.get("completed")]
    in_progress = [m for m in migrations if m.get("in_progress")]
    consumers_migrated = sum(m.get("consumers_migrated", 0) for m in migrations)
    return {"migrations": len(migrations), "completed": len(completed), "in_progress": len(in_progress),
            "consumers_migrated": consumers_migrated, "healthy": True}
