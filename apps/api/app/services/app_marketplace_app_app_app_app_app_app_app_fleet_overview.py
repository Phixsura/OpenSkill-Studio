"""Service fleet overview — high-level view of the entire service fleet."""
from __future__ import annotations
from collections import defaultdict


def fleet_overview(services: list[dict]) -> dict:
    by_status: dict[str, int] = defaultdict(int)
    by_tier: dict[str, int] = defaultdict(int)
    total_rps = 0
    for s in services:
        by_status[s.get("status", "unknown")] += 1
        by_tier[s.get("tier", "standard")] += 1
        total_rps += s.get("rps", 0)
    healthy = by_status.get("healthy", 0)
    health_pct = round(healthy / max(len(services), 1) * 100, 1)
    overall = "healthy" if health_pct >= 95 else ("degraded" if health_pct >= 70 else "critical")
    return {"overall": overall, "total": len(services), "by_status": dict(by_status),
            "by_tier": dict(by_tier), "health_pct": health_pct,
            "total_rps": total_rps}
