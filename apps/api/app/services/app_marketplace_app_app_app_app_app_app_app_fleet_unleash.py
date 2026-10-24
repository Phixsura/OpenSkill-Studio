"""Fleet Unleash — track open-source feature toggle metrics."""
from __future__ import annotations
def fleet_unleash_status(toggles: list[dict]) -> dict:
    enabled = [t for t in toggles if t.get("enabled", False)]
    stale = [t for t in toggles if t.get("stale", False)]
    impressions = sum(t.get("impressions_24h", 0) for t in toggles)
    return {"total": len(toggles), "enabled": len(enabled), "stale": len(stale),
            "impressions_24h": impressions, "healthy": len(stale) < 5}
