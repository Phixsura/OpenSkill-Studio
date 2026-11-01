"""Fleet Service Discovery v9 — track service registration and DNS resolution."""
from __future__ import annotations
def fleet_service_discovery_v9(services: list[dict]) -> dict:
    registered = [s for s in services if s.get("registered")]
    healthy_svc = [s for s in services if s.get("health") == "healthy"]
    endpoints = sum(s.get("endpoints", 0) for s in services)
    return {"services": len(services), "registered": len(registered), "healthy_services": len(healthy_svc),
            "total_endpoints": endpoints, "healthy": len(healthy_svc) == len(services)}
