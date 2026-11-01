"""Fleet API Load Shedding v9 — track adaptive load shedding."""
from __future__ import annotations
def fleet_api_load_shedding_v9(services: list[dict]) -> dict:
    shedding = [s for s in services if s.get("shedding_active")]
    shed_requests = sum(s.get("shed_today", 0) for s in services)
    total_requests = sum(s.get("total_today", 0) for s in services)
    return {"services": len(services), "shedding_active": len(shedding), "shed_today": shed_requests,
            "total_today": total_requests, "healthy": len(shedding) == 0}
