"""Fleet Node Pool v9 — track K8s node pool management."""
from __future__ import annotations
def fleet_node_pool_v9(pools: list[dict]) -> dict:
    ready = [p for p in pools if p.get("status") == "ready"]
    scaling = [p for p in pools if p.get("scaling")]
    nodes = sum(p.get("nodes", 0) for p in pools)
    return {"pools": len(pools), "ready": len(ready), "scaling": len(scaling),
            "total_nodes": nodes, "healthy": len(ready) == len(pools)}
