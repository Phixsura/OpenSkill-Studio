"""Fleet AI Marketplace v7 — track AI model and tool marketplace."""
from __future__ import annotations
def fleet_ai_marketplace_v7(marketplaces: list[dict]) -> dict:
    active = [m for m in marketplaces if m.get("active", True)]
    listings = sum(m.get("listings", 0) for m in marketplaces)
    downloads = sum(m.get("downloads_30d", 0) for m in marketplaces)
    publishers = sum(m.get("publishers", 0) for m in marketplaces)
    revenue = round(sum(m.get("revenue_usd", 0) for m in marketplaces), 2)
    return {"marketplaces": len(marketplaces), "active": len(active), "listings": listings,
            "downloads": downloads, "publishers": publishers, "revenue": revenue, "thriving": downloads > 100000}
