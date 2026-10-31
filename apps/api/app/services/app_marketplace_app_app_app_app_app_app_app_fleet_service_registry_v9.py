"""Fleet Service Registry v9 — track service registration and deregistration."""
from __future__ import annotations
def fleet_service_registry_v9(services: list[dict]) -> dict:
    registered = [s for s in services if s.get("registered")]
    healthy_s = [s for s in services if s.get("healthy")]
    instances = sum(s.get("instances", 0) for s in services)
    return {"services": len(services), "registered": len(registered), "healthy": len(healthy_s),
            "total_instances": instances, "all_healthy": len(healthy_s) == len(services)}
