"""Fleet Plausible — track privacy-friendly web analytics."""
from __future__ import annotations
def fleet_plausible_status(sites: list[dict]) -> dict:
    active = [s for s in sites if s.get("active", True)]
    pageviews_24h = sum(s.get("pageviews_24h", 0) for s in sites)
    visitors_24h = sum(s.get("visitors_24h", 0) for s in sites)
    return {"sites": len(sites), "active": len(active), "pageviews_24h": pageviews_24h,
            "visitors_24h": visitors_24h, "all_active": len(active) == len(sites)}
