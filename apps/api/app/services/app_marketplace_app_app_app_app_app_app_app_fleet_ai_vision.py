"""Fleet AI Vision — track computer vision service."""
from __future__ import annotations
def fleet_ai_vision(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    images_24h = sum(s.get("images_24h", 0) for s in services)
    detections = sum(s.get("detections_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "images_24h": images_24h,
            "detections_24h": detections, "all_active": len(active) == len(services)}
