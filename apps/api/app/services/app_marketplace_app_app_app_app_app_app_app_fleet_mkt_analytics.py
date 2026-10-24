"""Fleet marketplace analytics — track marketplace KPIs."""
from __future__ import annotations
def fleet_mkt_analytics(metrics: dict) -> dict:
    listings = metrics.get("total_listings", 0)
    installs = metrics.get("total_installs", 0)
    avg_rating = metrics.get("avg_rating", 0)
    install_rate = round(installs / max(listings, 1), 1)
    return {"listings": listings, "installs": installs, "avg_rating": avg_rating,
            "install_rate": install_rate, "healthy": avg_rating >= 4.0}
