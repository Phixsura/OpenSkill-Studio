"""Fleet Azure Container Apps — track serverless container platform."""
from __future__ import annotations
def fleet_aca_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running_status") == "Running"]
    replicas = sum(a.get("replicas", 0) for a in apps)
    revisions = sum(a.get("revisions", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "replicas": replicas,
            "revisions": revisions, "all_running": len(running) == len(apps)}
