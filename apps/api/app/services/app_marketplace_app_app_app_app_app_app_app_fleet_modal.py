"""Fleet Modal — track serverless GPU compute."""
from __future__ import annotations
def fleet_modal_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    gpu_hours = sum(a.get("gpu_hours_24h", 0) for a in apps)
    functions = sum(a.get("functions", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "gpu_hours_24h": round(gpu_hours, 1),
            "functions": functions, "all_running": len(running) == len(apps)}
