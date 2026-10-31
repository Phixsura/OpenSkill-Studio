"""Fleet Render — track Render platform service health."""
from __future__ import annotations
def fleet_render_status(services: list[dict]) -> dict:
    running = [s for s in services if s.get("status") == "running"]
    suspended = [s for s in services if s.get("suspended", False)]
    return {"services": len(services), "running": len(running), "suspended": len(suspended),
            "healthy": len(running) == len(services)}
