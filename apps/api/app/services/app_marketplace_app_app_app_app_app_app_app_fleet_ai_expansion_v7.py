"""Fleet AI Expansion v7 — track platform expansion and growth."""
from __future__ import annotations
def fleet_ai_expansion_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    new_markets = sum(t.get("markets", 0) for t in trackers)
    new_features = sum(t.get("features", 0) for t in trackers)
    expansion_rev = round(sum(t.get("expansion_usd", 0) for t in trackers), 2)
    return {"trackers": len(trackers), "active": len(active), "markets": new_markets,
            "features": new_features, "expansion_usd": expansion_rev, "expanding": new_markets > 0}
