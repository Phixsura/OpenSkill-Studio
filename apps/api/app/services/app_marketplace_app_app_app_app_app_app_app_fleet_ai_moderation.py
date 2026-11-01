"""Fleet AI Moderation — track content moderation."""
from __future__ import annotations
def fleet_ai_moderation(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    items_24h = sum(s.get("items_24h", 0) for s in services)
    flagged = sum(s.get("flagged_24h", 0) for s in services)
    flag_rate = round(flagged / max(items_24h, 1) * 100, 2)
    return {"services": len(services), "active": len(active), "items_24h": items_24h,
            "flagged_24h": flagged, "flag_rate_pct": flag_rate}
