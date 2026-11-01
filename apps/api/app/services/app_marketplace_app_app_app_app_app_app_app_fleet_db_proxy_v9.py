"""Fleet DB Proxy v9 — track database connection pooling and routing."""
from __future__ import annotations
def fleet_db_proxy_v9(pools: list[dict]) -> dict:
    active_conn = sum(p.get("active", 0) for p in pools)
    idle_conn = sum(p.get("idle", 0) for p in pools)
    max_conn = sum(p.get("max", 0) for p in pools)
    utilization = round(active_conn / max_conn * 100, 1) if max_conn else 0
    return {"pools": len(pools), "active": active_conn, "idle": idle_conn,
            "utilization_pct": utilization, "healthy": utilization < 85}
