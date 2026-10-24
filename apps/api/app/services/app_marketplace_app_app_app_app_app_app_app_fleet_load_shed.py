"""Fleet load shedding — track adaptive load shedding."""
from __future__ import annotations
def fleet_load_shedding(services: list[dict]) -> dict:
    shedding = [s for s in services if s.get("shedding_active", False)]
    total_shed = sum(s.get("requests_shed", 0) for s in services)
    return {"total": len(services), "shedding": len(shedding), "requests_shed": total_shed,
            "calm": len(shedding) == 0}
