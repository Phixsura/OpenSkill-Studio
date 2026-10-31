"""Fleet AI Marketplace v2 — track next-gen AI model marketplace."""
from __future__ import annotations
def fleet_ai_marketplace_v2(marketplaces: list[dict]) -> dict:
    active = [m for m in marketplaces if m.get("active", True)]
    listings = sum(m.get("listings", 0) for m in marketplaces)
    publishers = sum(m.get("publishers", 0) for m in marketplaces)
    installs_24h = sum(m.get("installs_24h", 0) for m in marketplaces)
    return {"marketplaces": len(marketplaces), "active": len(active), "listings": listings,
            "publishers": publishers, "installs_24h": installs_24h, "thriving": installs_24h > 1000}
