"""Fleet pool efficiency — track connection pool utilization efficiency."""
from __future__ import annotations
def fleet_pool_efficiency(pools: list[dict]) -> dict:
    total_active = sum(p.get("active", 0) for p in pools)
    total_idle = sum(p.get("idle", 0) for p in pools)
    total = total_active + total_idle
    efficiency = round(total_active / max(total, 1) * 100, 1)
    return {"active": total_active, "idle": total_idle, "efficiency_pct": efficiency,
            "wasteful": efficiency < 30}
