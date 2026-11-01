"""Fleet Analog — track Angular meta-framework."""
from __future__ import annotations
def fleet_analog_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    pages = sum(a.get("pages", 0) for a in apps)
    api_routes = sum(a.get("api_routes", 0) for a in apps)
    return {"apps": len(apps), "deployed": len(deployed), "pages": pages,
            "api_routes": api_routes, "fullstack": api_routes > 0}
