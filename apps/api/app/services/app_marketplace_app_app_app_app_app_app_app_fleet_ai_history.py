"""Fleet AI History — track AI interaction history."""
from __future__ import annotations
def fleet_ai_history(stores: list[dict]) -> dict:
    active = [s for s in stores if s.get("active", True)]
    interactions = sum(s.get("interactions", 0) for s in stores)
    storage_gb = sum(s.get("storage_gb", 0) for s in stores)
    return {"stores": len(stores), "active": len(active), "interactions": interactions,
            "storage_gb": round(storage_gb, 1), "all_active": len(active) == len(stores)}
