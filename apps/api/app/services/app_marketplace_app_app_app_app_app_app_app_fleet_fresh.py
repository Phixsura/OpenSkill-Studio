"""Fleet Fresh — track Deno Fresh framework health."""
from __future__ import annotations
def fleet_fresh_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    total_islands = sum(a.get("islands", 0) for a in apps)
    routes = sum(a.get("routes", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "islands": total_islands,
            "routes": routes, "all_running": len(running) == len(apps)}
