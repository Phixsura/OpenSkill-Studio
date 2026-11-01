"""Fleet Pulsar — track distributed messaging health."""
from __future__ import annotations
def fleet_pulsar_status(clusters: list[dict]) -> dict:
    healthy = [c for c in clusters if c.get("healthy", True)]
    topics = sum(c.get("topics", 0) for c in clusters)
    msg_rate = sum(c.get("msg_per_sec", 0) for c in clusters)
    return {"clusters": len(clusters), "healthy": len(healthy), "topics": topics,
            "msg_per_sec": msg_rate, "all_healthy": len(healthy) == len(clusters)}
