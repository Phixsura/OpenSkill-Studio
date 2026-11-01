"""Fleet DB Connection Monitor v9 — track database connection health."""
from __future__ import annotations
def fleet_db_connection_monitor_v9(pools: list[dict]) -> dict:
    active = sum(p.get("active", 0) for p in pools)
    idle = sum(p.get("idle", 0) for p in pools)
    max_c = sum(p.get("max", 0) for p in pools)
    waiting = sum(p.get("waiting", 0) for p in pools)
    utilization = round(active / max_c * 100, 1) if max_c else 0
    return {"pools": len(pools), "active": active, "idle": idle, "max": max_c,
            "waiting": waiting, "utilization_pct": utilization, "healthy": waiting == 0 and utilization < 85}
