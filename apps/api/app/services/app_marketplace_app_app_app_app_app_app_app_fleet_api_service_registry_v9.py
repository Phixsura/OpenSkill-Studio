"""Fleet API Service Registry v9 — track API-level service registration."""
from __future__ import annotations
def fleet_api_service_registry_v9(services: list[dict]) -> dict:
    registered = [s for s in services if s.get("registered")]
    healthy_s = [s for s in services if s.get("healthy")]
    versions = len({s.get("version") for s in services if s.get("version")})
    return {"services": len(services), "registered": len(registered), "healthy": len(healthy_s),
            "versions": versions, "all_healthy": len(healthy_s) == len(services)}
