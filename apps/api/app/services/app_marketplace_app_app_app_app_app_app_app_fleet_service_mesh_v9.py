"""Fleet Service Mesh v9 — track service-to-service communication health."""
from __future__ import annotations
def fleet_service_mesh_v9(services: list[dict]) -> dict:
    connected = [s for s in services if s.get("connected", True)]
    rps = sum(s.get("rps", 0) for s in services)
    error_rate = sum(s.get("error_rate", 0) for s in services) / len(services) if services else 0
    return {"services": len(services), "connected": len(connected), "total_rps": rps,
            "avg_error_rate": round(error_rate, 3),
            "healthy": error_rate < 1.0}
