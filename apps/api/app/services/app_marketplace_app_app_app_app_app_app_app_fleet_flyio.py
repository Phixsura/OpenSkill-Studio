"""Fleet Fly.io — track edge application deployment."""
from __future__ import annotations
def fleet_flyio_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("status") == "running"]
    machines = sum(a.get("machines", 0) for a in apps)
    regions = len(set(r for a in apps for r in a.get("regions", [])))
    return {"apps": len(apps), "running": len(running), "machines": machines,
            "regions": regions, "all_running": len(running) == len(apps)}
