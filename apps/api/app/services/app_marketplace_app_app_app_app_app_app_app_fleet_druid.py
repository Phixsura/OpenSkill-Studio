"""Fleet Druid — track real-time analytics database."""
from __future__ import annotations
def fleet_druid_status(clusters: list[dict]) -> dict:
    healthy = [c for c in clusters if c.get("healthy", True)]
    segments = sum(c.get("segments", 0) for c in clusters)
    queries_per_sec = sum(c.get("qps", 0) for c in clusters)
    return {"clusters": len(clusters), "healthy": len(healthy), "segments": segments,
            "qps": queries_per_sec, "all_healthy": len(healthy) == len(clusters)}
