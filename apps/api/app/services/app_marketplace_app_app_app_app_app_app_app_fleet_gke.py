"""Fleet GKE Autopilot — track managed Kubernetes health."""
from __future__ import annotations
def fleet_gke_status(clusters: list[dict]) -> dict:
    running = [c for c in clusters if c.get("status") == "RUNNING"]
    total_pods = sum(c.get("pods", 0) for c in clusters)
    autopilot = [c for c in clusters if c.get("autopilot", False)]
    return {"clusters": len(clusters), "running": len(running), "pods": total_pods,
            "autopilot": len(autopilot), "all_running": len(running) == len(clusters)}
