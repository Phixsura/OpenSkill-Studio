"""Fleet SolidStart — track reactive full-stack framework."""
from __future__ import annotations
def fleet_solidstart_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    routes = sum(a.get("routes", 0) for a in apps)
    signals = sum(a.get("signals", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "routes": routes,
            "signals": signals, "reactive": True}
