"""Fleet Cluster Autoscale v9 — track node-level cluster autoscaling."""
from __future__ import annotations
def fleet_cluster_autoscale_v9(clusters: list[dict]) -> dict:
    nodes = sum(c.get("nodes", 0) for c in clusters)
    min_nodes = sum(c.get("min_nodes", 0) for c in clusters)
    max_nodes = sum(c.get("max_nodes", 0) for c in clusters)
    return {"clusters": len(clusters), "total_nodes": nodes, "min": min_nodes,
            "max": max_nodes, "healthy": nodes >= min_nodes}
