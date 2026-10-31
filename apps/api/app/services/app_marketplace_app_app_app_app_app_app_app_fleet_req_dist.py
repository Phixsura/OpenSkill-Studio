"""Fleet request distribution — traffic distribution across regions."""
from __future__ import annotations
def fleet_request_distribution(regions: list[dict]) -> dict:
    total = sum(r.get("requests", 0) for r in regions)
    dist = {r["region"]: round(r.get("requests", 0) / max(total, 1) * 100, 1) for r in regions if "region" in r}
    hotspot = max(dist, key=lambda k: dist[k]) if dist else None
    return {"total_requests": total, "distribution": dist, "regions": len(regions), "hotspot": hotspot}
