"""Fleet Spark — track distributed compute cluster health."""
from __future__ import annotations
def fleet_spark_status(clusters: list[dict]) -> dict:
    running = [c for c in clusters if c.get("state") == "RUNNING"]
    total_executors = sum(c.get("executors", 0) for c in clusters)
    active_jobs = sum(c.get("active_jobs", 0) for c in clusters)
    return {"clusters": len(clusters), "running": len(running), "executors": total_executors,
            "active_jobs": active_jobs, "all_running": len(running) == len(clusters)}
