"""Fleet Service Scaling v9 — track service scaling decisions and history."""
from __future__ import annotations
def fleet_service_scaling_v9(services: list[dict]) -> dict:
    scaled_up = [s for s in services if s.get("last_action") == "scale_up"]
    scaled_down = [s for s in services if s.get("last_action") == "scale_down"]
    total_replicas = sum(s.get("replicas", 0) for s in services)
    return {"services": len(services), "scaled_up": len(scaled_up), "scaled_down": len(scaled_down),
            "total_replicas": total_replicas, "healthy": True}
