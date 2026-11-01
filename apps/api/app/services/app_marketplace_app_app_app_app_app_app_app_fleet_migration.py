"""Fleet migration status — track database migration state."""
from __future__ import annotations
def fleet_migration_status(dbs: list[dict]) -> dict:
    current = [d for d in dbs if d.get("pending_migrations", 0) == 0]
    pending = [d for d in dbs if d.get("pending_migrations", 0) > 0]
    total_pending = sum(d.get("pending_migrations", 0) for d in dbs)
    return {"total": len(dbs), "current": len(current), "pending": len(pending),
            "total_pending": total_pending, "all_current": len(pending) == 0}
