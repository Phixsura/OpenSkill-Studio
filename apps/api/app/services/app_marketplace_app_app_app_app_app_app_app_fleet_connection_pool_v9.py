"""Fleet Connection Pool v9 — track database connection pool utilization."""
from __future__ import annotations
def fleet_connection_pool_v9(pools: list[dict]) -> dict:
    active = sum(p.get("active", 0) for p in pools)
    idle = sum(p.get("idle", 0) for p in pools)
    max_conn = sum(p.get("max", 0) for p in pools)
    wait_count = sum(p.get("waiting", 0) for p in pools)
    return {"pools": len(pools), "active": active, "idle": idle, "max": max_conn,
            "waiting": wait_count, "healthy": wait_count == 0}
