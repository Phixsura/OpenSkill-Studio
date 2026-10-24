"""Fleet AI Platform Leadership v7 — track AI platform market leadership."""
from __future__ import annotations
def fleet_ai_platform_leadership_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    market_rank = min((t.get("rank", 999) for t in trackers), default=999)
    awards = sum(t.get("awards", 0) for t in trackers)
    analyst_rating = round(sum(t.get("rating", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "rank": market_rank,
            "awards": awards, "rating": analyst_rating, "leader": market_rank <= 3}
