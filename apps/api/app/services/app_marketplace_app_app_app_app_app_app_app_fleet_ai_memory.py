"""Fleet AI Memory — track long-term AI conversation memory."""
from __future__ import annotations
def fleet_ai_memory(stores: list[dict]) -> dict:
    active = [s for s in stores if s.get("active", True)]
    memories = sum(s.get("memories", 0) for s in stores)
    retrievals_24h = sum(s.get("retrievals_24h", 0) for s in stores)
    return {"stores": len(stores), "active": len(active), "memories": memories,
            "retrievals_24h": retrievals_24h, "all_active": len(active) == len(stores)}
