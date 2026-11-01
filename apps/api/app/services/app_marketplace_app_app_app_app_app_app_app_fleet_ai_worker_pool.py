"""Fleet AI Worker Pool — track distributed AI compute worker management."""
from __future__ import annotations
def fleet_ai_worker_pool(pools: list[dict]) -> dict:
    active = [p for p in pools if p.get("active", True)]
    workers = sum(p.get("workers", 0) for p in pools)
    busy = sum(p.get("busy", 0) for p in pools)
    idle = workers - busy
    utilization = round(busy / max(workers, 1) * 100, 1)
    return {"pools": len(pools), "active": len(active), "workers": workers,
            "busy": busy, "idle": idle, "utilization": utilization, "efficient": utilization > 70}
