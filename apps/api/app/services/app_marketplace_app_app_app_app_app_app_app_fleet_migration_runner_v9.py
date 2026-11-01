"""Fleet Migration Runner v9 — track database migration execution."""
from __future__ import annotations
def fleet_migration_runner_v9(migrations: list[dict]) -> dict:
    applied = [m for m in migrations if m.get("applied")]
    pending = [m for m in migrations if not m.get("applied")]
    rollbacks = [m for m in migrations if m.get("rolled_back")]
    return {"total": len(migrations), "applied": len(applied), "pending": len(pending),
            "rollbacks": len(rollbacks), "healthy": len(pending) == 0}
