"""Geo distribution tracker — track user and request geography."""
from __future__ import annotations

REGIONS = {
    "us-east": {"name": "US East", "lat": 39.0, "lon": -77.0},
    "us-west": {"name": "US West", "lat": 37.3, "lon": -121.9},
    "eu-west": {"name": "EU West", "lat": 53.3, "lon": -6.3},
    "eu-central": {"name": "EU Central", "lat": 50.1, "lon": 8.7},
    "ap-southeast": {"name": "Asia Pacific SE", "lat": 1.3, "lon": 103.8},
    "ap-northeast": {"name": "Asia Pacific NE", "lat": 35.7, "lon": 139.7},
}


def aggregate_geo(requests: list[dict]) -> dict:
    by_region: dict[str, int] = {}
    for r in requests:
        region = r.get("region", "unknown")
        by_region[region] = by_region.get(region, 0) + 1
    total = sum(by_region.values())
    distribution = []
    for region, count in sorted(by_region.items(), key=lambda x: -x[1]):
        info = REGIONS.get(region, {"name": region})
        pct = round(count / max(total, 1) * 100, 1)
        distribution.append({"region": region, "name": info.get("name", region),
                             "count": count, "pct": pct})
    top = distribution[0]["region"] if distribution else None
    return {"distribution": distribution, "total": total,
            "region_count": len(by_region), "top_region": top}
