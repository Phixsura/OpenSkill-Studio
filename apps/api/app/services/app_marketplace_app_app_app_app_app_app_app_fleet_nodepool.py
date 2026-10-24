"""Fleet node pool — track node pool utilization and capacity."""
from __future__ import annotations
def fleet_nodepool_utilization(pools: list[dict]) -> dict:
    total_nodes = sum(p.get("nodes", 0) for p in pools)
    total_capacity = sum(p.get("max_nodes", 0) for p in pools)
    pct = round(total_nodes / max(total_capacity, 1) * 100, 1)
    at_max = [p for p in pools if p.get("nodes", 0) >= p.get("max_nodes", 999)]
    return {"pools": len(pools), "total_nodes": total_nodes, "capacity": total_capacity,
            "util_pct": pct, "at_max": len(at_max)}
