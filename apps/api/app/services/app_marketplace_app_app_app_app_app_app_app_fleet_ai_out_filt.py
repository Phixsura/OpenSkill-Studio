"""Fleet AI Output Filter v2 — track AI response content filtering."""
from __future__ import annotations
def fleet_ai_output_filter_v2(filters: list[dict]) -> dict:
    active = [f for f in filters if f.get("active", True)]
    filtered_24h = sum(f.get("filtered_24h", 0) for f in filters)
    blocked_24h = sum(f.get("blocked_24h", 0) for f in filters)
    rules = sum(f.get("rules", 0) for f in filters)
    return {"filters": len(filters), "active": len(active), "filtered_24h": filtered_24h,
            "blocked_24h": blocked_24h, "rules": rules, "guarding": rules > 0}
