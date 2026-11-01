"""Fleet Cloud Migration v9 — track workload cloud migration progress."""
from __future__ import annotations
def fleet_cloud_migration_v9(workloads: list[dict]) -> dict:
    migrated = [w for w in workloads if w.get("migrated")]
    in_progress = [w for w in workloads if w.get("status") == "migrating"]
    remaining = [w for w in workloads if w.get("status") == "pending"]
    return {"total": len(workloads), "migrated": len(migrated), "in_progress": len(in_progress),
            "remaining": len(remaining), "healthy": len(remaining) < len(workloads) * 0.1}
