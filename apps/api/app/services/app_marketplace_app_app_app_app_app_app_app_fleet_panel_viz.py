"""Fleet Panel — track data visualization dashboards."""
from __future__ import annotations
def fleet_panel_status(apps: list[dict]) -> dict:
    running = [a for a in apps if a.get("running", True)]
    widgets = sum(a.get("widgets", 0) for a in apps)
    sessions = sum(a.get("sessions_24h", 0) for a in apps)
    return {"apps": len(apps), "running": len(running), "widgets": widgets,
            "sessions_24h": sessions, "all_running": len(running) == len(apps)}
