"""Fleet AI Intent — track intent classification for conversational AI."""
from __future__ import annotations
def fleet_ai_intent(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    classifications_24h = sum(s.get("classifications_24h", 0) for s in services)
    intents = sum(s.get("intents_defined", 0) for s in services)
    return {"services": len(services), "active": len(active), "classifications_24h": classifications_24h,
            "intents": intents, "all_active": len(active) == len(services)}
