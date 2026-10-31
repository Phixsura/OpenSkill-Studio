"""Fleet Cluster Health v9 — track Kubernetes cluster overall health."""
from __future__ import annotations
def fleet_cluster_health_v9(clusters: list[dict]) -> dict:
    healthy_c = [c for c in clusters if c.get("status") == "healthy"]
    nodes = sum(c.get("nodes", 0) for c in clusters)
    pods = sum(c.get("pods", 0) for c in clusters)
    cpu_pct = sum(c.get("cpu_pct", 0) for c in clusters) / len(clusters) if clusters else 0
    return {"clusters": len(clusters), "healthy_clusters": len(healthy_c), "total_nodes": nodes,
            "total_pods": pods, "avg_cpu_pct": round(cpu_pct, 1), "healthy": len(healthy_c) == len(clusters)}
