"""Fleet .NET Aspire — track cloud-native .NET app health."""
from __future__ import annotations
def fleet_aspire_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    total_services = sum(a.get("services", 0) for a in apps)
    resources = sum(a.get("resources", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "services": total_services,
            "resources": resources, "all_running": len(running) == len(apps)}
