"""Availability zones manager — track multi-AZ deployment status."""
from __future__ import annotations


def check_zone_health(zones: list[dict]) -> dict:
    healthy = sum(1 for z in zones if z.get("status") == "healthy")
    by_region: dict[str, list[str]] = {}
    for z in zones:
        region = z.get("region", "unknown")
        by_region.setdefault(region, []).append(z["name"])
    return {"total_zones": len(zones), "healthy": healthy,
            "unhealthy": len(zones) - healthy, "regions": len(by_region),
            "by_region": {r: len(zs) for r, zs in by_region.items()},
            "multi_az": len(zones) >= 2, "all_healthy": healthy == len(zones)}
