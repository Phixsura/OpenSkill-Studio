"""Fleet thread pool — monitor thread pool utilization."""
from __future__ import annotations
def fleet_thread_pool(services: list[dict]) -> dict:
    active = sum(s.get("active_threads", 0) for s in services)
    total = sum(s.get("max_threads", 1) for s in services)
    pct = round(active / max(total, 1) * 100, 1)
    return {"active": active, "max": total, "pct": pct, "exhausted": pct > 90}
