"""Fleet Fargate — track serverless container compute."""
from __future__ import annotations
def fleet_fargate_status(tasks: list[dict]) -> dict:
    running = [t for t in tasks if t.get("status") == "RUNNING"]
    cpu_units = sum(t.get("cpu", 0) for t in running)
    memory_mb = sum(t.get("memory_mb", 0) for t in running)
    return {"total_tasks": len(tasks), "running": len(running), "cpu_units": cpu_units,
            "memory_mb": memory_mb, "all_running": len(running) == len(tasks)}
