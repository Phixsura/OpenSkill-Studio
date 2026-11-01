"""Fleet blue-green deploy — track blue/green deployment state."""
from __future__ import annotations
def fleet_bluegreen_status(deploys: list[dict]) -> dict:
    live = [d for d in deploys if d.get("active") == "green"]
    standby = [d for d in deploys if d.get("active") == "blue"]
    switching = [d for d in deploys if d.get("status") == "switching"]
    return {"total": len(deploys), "green_live": len(live), "blue_live": len(standby),
            "switching": len(switching), "stable": len(switching) == 0}
