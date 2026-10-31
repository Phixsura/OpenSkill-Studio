"""Fleet Service Catalog v9 — track registered microservices and ownership."""
from __future__ import annotations
def fleet_service_catalog_v9(services: list[dict]) -> dict:
    active = [s for s in services if s.get("status") == "active"]
    teams = len({s.get("team") for s in services if s.get("team")})
    tier1 = [s for s in services if s.get("tier") == 1]
    return {"total": len(services), "active": len(active), "teams": teams,
            "tier1_critical": len(tier1), "healthy": len(active) == len(services)}
