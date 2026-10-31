"""Fleet Railway — track Railway deployment health."""
from __future__ import annotations
def fleet_railway_status(services: list[dict]) -> dict:
    deployed = [s for s in services if s.get("status") == "SUCCESS"]
    total_deploys = sum(s.get("deploys_24h", 0) for s in services)
    return {"services": len(services), "deployed": len(deployed), "deploys_24h": total_deploys,
            "all_healthy": len(deployed) == len(services)}
