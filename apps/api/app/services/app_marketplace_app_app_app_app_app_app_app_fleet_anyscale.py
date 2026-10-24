"""Fleet Anyscale — track Ray cluster management."""
from __future__ import annotations
def fleet_anyscale_status(clusters: list[dict]) -> dict:
    running = [c for c in clusters if c.get("status") == "RUNNING"]
    nodes = sum(c.get("nodes", 0) for c in clusters)
    ray_jobs = sum(c.get("active_jobs", 0) for c in clusters)
    return {"clusters": len(clusters), "running": len(running), "nodes": nodes,
            "active_jobs": ray_jobs, "all_running": len(running) == len(clusters)}
