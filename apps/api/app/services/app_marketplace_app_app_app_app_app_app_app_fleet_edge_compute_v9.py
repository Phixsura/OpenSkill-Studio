"""Fleet Edge Compute v9 — track edge node deployments worldwide."""
from __future__ import annotations
def fleet_edge_compute_v9(nodes: list[dict]) -> dict:
    active = [n for n in nodes if n.get("active", True)]
    latency = sum(n.get("latency_ms", 0) for n in nodes)
    avg = latency / len(nodes) if nodes else 0
    return {"total": len(nodes), "active": len(active), "avg_latency_ms": round(avg, 2),
            "regions": len({n.get("region") for n in nodes if n.get("region")}),
            "healthy": len(active) == len(nodes)}
