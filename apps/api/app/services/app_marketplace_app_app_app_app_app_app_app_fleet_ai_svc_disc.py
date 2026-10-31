"""Fleet AI Service Discovery — track dynamic AI service registration."""
from __future__ import annotations
def fleet_ai_service_discovery(registries: list[dict]) -> dict:
    active = [r for r in registries if r.get("active", True)]
    services = sum(r.get("services", 0) for r in registries)
    instances = sum(r.get("instances", 0) for r in registries)
    lookups_24h = sum(r.get("lookups_24h", 0) for r in registries)
    return {"registries": len(registries), "active": len(active), "services": services,
            "instances": instances, "lookups_24h": lookups_24h, "discoverable": services > 0}
