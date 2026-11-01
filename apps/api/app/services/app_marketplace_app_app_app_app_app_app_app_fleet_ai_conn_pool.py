"""Fleet AI Connection Pool — track AI backend connection management."""
from __future__ import annotations
def fleet_ai_connection_pool(pools: list[dict]) -> dict:
    active = [p for p in pools if p.get("active", True)]
    max_conns = sum(p.get("max_connections", 0) for p in pools)
    active_conns = sum(p.get("active_connections", 0) for p in pools)
    utilization = round(active_conns / max(max_conns, 1) * 100, 1)
    return {"pools": len(pools), "active": len(active), "max": max_conns,
            "active_conns": active_conns, "utilization": utilization, "healthy": utilization < 80}
