"""Geo-routing controller — route requests to nearest regional endpoint."""
from __future__ import annotations
import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def route_to_nearest(client_lat: float, client_lon: float, regions: list[dict]) -> dict:
    best = None
    best_dist = float("inf")
    for r in regions:
        if r.get("status") != "healthy":
            continue
        dist = haversine_km(client_lat, client_lon, r["lat"], r["lon"])
        if dist < best_dist:
            best_dist = dist
            best = r
    if not best:
        return {"routed": False, "reason": "no_healthy_region"}
    return {"routed": True, "region": best["name"], "endpoint": best.get("endpoint", ""),
            "distance_km": round(best_dist, 1)}


def region_health(regions: list[dict]) -> dict:
    healthy = sum(1 for r in regions if r.get("status") == "healthy")
    return {"total": len(regions), "healthy": healthy, "unhealthy": len(regions) - healthy}
