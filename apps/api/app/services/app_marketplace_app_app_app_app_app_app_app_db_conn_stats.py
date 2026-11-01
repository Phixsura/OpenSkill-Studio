"""Database connection stats — monitor database connection health."""
from __future__ import annotations


def analyze_connections(pools: list[dict]) -> dict:
    total_active = sum(p.get("active", 0) for p in pools)
    total_idle = sum(p.get("idle", 0) for p in pools)
    total_max = sum(p.get("max_size", 0) for p in pools)
    total_waiting = sum(p.get("waiting", 0) for p in pools)
    utilization = round(total_active / max(total_max, 1) * 100, 1)
    health = "healthy" if utilization < 70 else "busy" if utilization < 90 else "saturated"
    return {"pools": len(pools), "active": total_active, "idle": total_idle,
            "max": total_max, "waiting": total_waiting,
            "utilization_pct": utilization, "health": health}


def pool_recommendations(stats: dict) -> list[str]:
    recs = []
    if stats["utilization_pct"] > 80:
        recs.append("Consider increasing max pool size")
    if stats["waiting"] > 0:
        recs.append(f"{stats['waiting']} queries waiting — add connection capacity")
    if stats["idle"] > stats["active"] * 3:
        recs.append("High idle count — reduce min pool size to save resources")
    return recs
