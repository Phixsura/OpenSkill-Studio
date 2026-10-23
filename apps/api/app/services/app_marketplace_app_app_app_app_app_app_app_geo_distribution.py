"""Geo distribution analyzer — map users/requests by region."""
from __future__ import annotations
import math

REGIONS = {
    "us-east": {"lat": 39.0, "lon": -77.5, "label": "US East"},
    "us-west": {"lat": 37.8, "lon": -122.4, "label": "US West"},
    "eu-west": {"lat": 51.5, "lon": -0.1, "label": "Europe West"},
    "eu-central": {"lat": 50.1, "lon": 8.7, "label": "Europe Central"},
    "ap-east": {"lat": 35.7, "lon": 139.7, "label": "Asia Pacific"},
    "ap-south": {"lat": 19.1, "lon": 72.9, "label": "India"},
}


def analyze_distribution(requests: list[dict]) -> dict:
    by_region: dict[str, int] = {}
    total = len(requests)
    for req in requests:
        region = req.get("region", "unknown")
        by_region[region] = by_region.get(region, 0) + 1
    regions = []
    for region, count in sorted(by_region.items(), key=lambda x: -x[1]):
        info = REGIONS.get(region, {})
        regions.append({
            "region": region, "label": info.get("label", region),
            "count": count, "pct": round(count / max(total, 1) * 100, 1),
            "lat": info.get("lat"), "lon": info.get("lon"),
        })
    top = regions[0]["region"] if regions else None
    return {"total": total, "regions": regions, "top_region": top,
            "unique_regions": len(regions)}


def find_nearest_region(lat: float, lon: float) -> dict:
    best = None
    best_dist = float("inf")
    for key, info in REGIONS.items():
        d = math.sqrt((lat - info["lat"]) ** 2 + (lon - info["lon"]) ** 2)
        if d < best_dist:
            best_dist = d
            best = key
    return {"nearest": best, "label": REGIONS[best]["label"], "distance_approx": round(best_dist, 1)}
