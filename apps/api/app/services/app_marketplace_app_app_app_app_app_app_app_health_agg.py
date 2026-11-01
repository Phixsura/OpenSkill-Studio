"""Health check aggregator — aggregate health status across all services."""
from __future__ import annotations
import time


def aggregate_health(checks: list[dict]) -> dict:
    up = [c for c in checks if c.get("status") == "up"]
    down = [c for c in checks if c.get("status") == "down"]
    degraded = [c for c in checks if c.get("status") == "degraded"]
    overall = "healthy" if not down and not degraded else (
        "outage" if len(down) > len(checks) // 2 else "degraded")
    avg_latency = round(sum(c.get("latency_ms", 0) for c in checks) / max(len(checks), 1), 1)
    return {"overall": overall, "up": len(up), "down": len(down),
            "degraded": len(degraded), "total": len(checks),
            "avg_latency_ms": avg_latency, "uptime_pct": round(len(up) / max(len(checks), 1) * 100, 1)}


def health_history(snapshots: list[dict]) -> dict:
    if not snapshots:
        return {"snapshots": 0, "trend": "unknown"}
    recent = snapshots[-1]["uptime_pct"] if snapshots else 0
    prev = snapshots[-2]["uptime_pct"] if len(snapshots) > 1 else recent
    trend = "improving" if recent > prev else ("declining" if recent < prev else "stable")
    return {"snapshots": len(snapshots), "latest_uptime": recent,
            "previous_uptime": prev, "trend": trend}
