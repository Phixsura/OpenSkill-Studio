"""Fleet NestJS — track enterprise Node.js framework."""
from __future__ import annotations
def fleet_nestjs_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    total_modules = sum(a.get("modules", 0) for a in apps)
    total_endpoints = sum(a.get("endpoints", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "modules": total_modules,
            "endpoints": total_endpoints, "all_running": len(running) == len(apps)}
