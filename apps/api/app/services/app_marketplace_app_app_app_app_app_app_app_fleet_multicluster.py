"""Fleet multi-cluster — track health across multiple k8s clusters."""
from __future__ import annotations
def fleet_multicluster(clusters: list[dict]) -> dict:
    healthy = [c for c in clusters if c.get("status") == "healthy"]
    degraded = [c for c in clusters if c.get("status") == "degraded"]
    return {"total": len(clusters), "healthy": len(healthy), "degraded": len(degraded),
            "down": len(clusters) - len(healthy) - len(degraded), "all_ok": len(healthy) == len(clusters)}
