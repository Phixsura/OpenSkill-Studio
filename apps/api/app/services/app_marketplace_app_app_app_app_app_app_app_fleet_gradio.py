"""Fleet Gradio — track ML demo interface platform."""
from __future__ import annotations
def fleet_gradio_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    interfaces = sum(a.get("interfaces", 0) for a in apps)
    users_24h = sum(a.get("users_24h", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "interfaces": interfaces,
            "users_24h": users_24h, "all_running": len(running) == len(apps)}
