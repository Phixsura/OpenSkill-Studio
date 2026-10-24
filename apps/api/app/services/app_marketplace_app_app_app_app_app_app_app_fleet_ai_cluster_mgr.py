"""Fleet AI Cluster Manager — track AI compute cluster lifecycle."""
from __future__ import annotations
def fleet_ai_cluster_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    clusters = sum(m.get("clusters", 0) for m in managers)
    nodes = sum(m.get("nodes", 0) for m in managers)
    utilization = round(sum(m.get("util_pct", 0) for m in managers) / max(len(managers), 1), 1)
    return {"managers": len(managers), "active": len(active), "clusters": clusters,
            "nodes": nodes, "utilization": utilization, "efficient": utilization > 70}
