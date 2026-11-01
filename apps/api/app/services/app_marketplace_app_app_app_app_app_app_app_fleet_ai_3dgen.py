"""Fleet AI 3D Gen — track 3D model generation."""
from __future__ import annotations
def fleet_ai_3dgen(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    models_24h = sum(s.get("models_24h", 0) for s in services)
    vertices_generated = sum(s.get("vertices_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "models_24h": models_24h,
            "vertices_24h": vertices_generated, "all_active": len(active) == len(services)}
