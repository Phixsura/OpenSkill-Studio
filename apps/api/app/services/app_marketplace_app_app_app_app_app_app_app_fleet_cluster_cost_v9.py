"""Fleet Cluster Cost v9 — track per-cluster infrastructure costs."""
from __future__ import annotations
def fleet_cluster_cost_v9(clusters: list[dict]) -> dict:
    total = sum(c.get("monthly_cost", 0) for c in clusters)
    compute = sum(c.get("compute_cost", 0) for c in clusters)
    storage = sum(c.get("storage_cost", 0) for c in clusters)
    network = sum(c.get("network_cost", 0) for c in clusters)
    return {"clusters": len(clusters), "total_monthly": round(total, 2), "compute": round(compute, 2),
            "storage": round(storage, 2), "network": round(network, 2), "healthy": True}
