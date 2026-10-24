"""Database connection monitor — monitor active DB connections."""
from __future__ import annotations


def monitor_connections(pools: list[dict]) -> dict:
    total_active = sum(p.get("active", 0) for p in pools)
    total_max = sum(p.get("max_size", 0) for p in pools)
    utilization = round(total_active / max(total_max, 1) * 100, 1)
    saturated = [p["name"] for p in pools if p.get("active", 0) >= p.get("max_size", 1) * 0.9]
    return {"total_active": total_active, "total_max": total_max,
            "utilization_pct": utilization, "pools": len(pools),
            "saturated_pools": saturated,
            "healthy": len(saturated) == 0}


def connection_trend(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"trend": "stable", "data_points": len(snapshots)}
    recent = snapshots[-1]["active"]
    prev = snapshots[-2]["active"]
    delta = recent - prev
    trend = "increasing" if delta > 5 else ("decreasing" if delta < -5 else "stable")
    return {"trend": trend, "current": recent, "previous": prev, "delta": delta}
