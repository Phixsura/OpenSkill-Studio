"""Fleet API Versioning v9 — track API version lifecycle and deprecation."""
from __future__ import annotations
def fleet_api_versioning_v9(apis: list[dict]) -> dict:
    active = [a for a in apis if a.get("status") == "active"]
    deprecated = [a for a in apis if a.get("status") == "deprecated"]
    sunset = [a for a in apis if a.get("status") == "sunset"]
    return {"total": len(apis), "active": len(active), "deprecated": len(deprecated),
            "sunset": len(sunset), "healthy": len(sunset) == 0}
