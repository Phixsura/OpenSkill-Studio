"""Fleet Amplitude — track digital analytics platform."""
from __future__ import annotations
def fleet_amplitude_status(orgs: list[dict]) -> dict:
    active = [o for o in orgs if o.get("active", True)]
    events_24h = sum(o.get("events_24h", 0) for o in orgs)
    charts = sum(o.get("charts", 0) for o in orgs)
    return {"orgs": len(orgs), "active": len(active), "events_24h": events_24h,
            "charts": charts, "all_active": len(active) == len(orgs)}
