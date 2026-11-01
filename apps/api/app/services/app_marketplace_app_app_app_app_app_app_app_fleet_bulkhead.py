"""Fleet bulkhead — track bulkhead isolation patterns."""
from __future__ import annotations
def fleet_bulkhead(pools: list[dict]) -> dict:
    active = sum(p.get("active_threads", 0) for p in pools)
    max_threads = sum(p.get("max_threads", 0) for p in pools)
    rejected = sum(p.get("rejected", 0) for p in pools)
    pct = round(active / max(max_threads, 1) * 100, 1)
    return {"pools": len(pools), "active": active, "max": max_threads,
            "rejected": rejected, "util_pct": pct, "healthy": rejected == 0}
