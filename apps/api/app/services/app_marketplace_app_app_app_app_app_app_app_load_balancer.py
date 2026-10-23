"""Load balancer health checker — monitor backend instances and routing."""
from __future__ import annotations


def check_backends(backends: list[dict]) -> dict:
    healthy = [b for b in backends if b.get("healthy", False)]
    unhealthy = [b for b in backends if not b.get("healthy", False)]
    total_rps = sum(b.get("rps", 0) for b in healthy)
    avg_latency = round(sum(b.get("latency_ms", 0) for b in healthy) / max(len(healthy), 1), 1)
    weights = {}
    for b in healthy:
        w = b.get("weight", 1)
        weights[b["id"]] = {"weight": w, "traffic_pct": round(w / max(sum(hb.get("weight", 1) for hb in healthy), 1) * 100, 1)}
    return {
        "total": len(backends), "healthy": len(healthy), "unhealthy": len(unhealthy),
        "status": "healthy" if not unhealthy else "degraded" if healthy else "down",
        "total_rps": total_rps, "avg_latency_ms": avg_latency,
        "routing": weights,
        "backends": [{"id": b["id"], "healthy": b.get("healthy", False),
                       "rps": b.get("rps", 0), "latency_ms": b.get("latency_ms", 0)}
                      for b in backends],
    }


def recommend_scaling(backends: list[dict], *, target_rps_per_instance: int = 1000) -> dict:
    healthy = [b for b in backends if b.get("healthy", False)]
    total_rps = sum(b.get("rps", 0) for b in healthy)
    current = len(healthy)
    recommended = max(1, -(-total_rps // target_rps_per_instance))  # ceil division
    action = "scale_up" if recommended > current else "scale_down" if recommended < current else "none"
    return {"current_instances": current, "recommended": recommended,
            "action": action, "total_rps": total_rps, "target_per_instance": target_rps_per_instance}
