"""Fleet API Health Endpoint v9 — track /health endpoint standardization."""
from __future__ import annotations
def fleet_api_health_endpoint_v9(services: list[dict]) -> dict:
    with_health = [s for s in services if s.get("health_endpoint")]
    with_readiness = [s for s in services if s.get("readiness_endpoint")]
    with_liveness = [s for s in services if s.get("liveness_endpoint")]
    return {"services": len(services), "health": len(with_health), "readiness": len(with_readiness),
            "liveness": len(with_liveness), "healthy": len(with_health) == len(services)}
