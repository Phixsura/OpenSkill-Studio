"""Fleet AI Video Generation — track video synthesis."""
from __future__ import annotations
def fleet_ai_videogen(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    videos_24h = sum(s.get("videos_24h", 0) for s in services)
    minutes_generated = sum(s.get("minutes_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "videos_24h": videos_24h,
            "minutes_24h": minutes_generated, "all_active": len(active) == len(services)}
