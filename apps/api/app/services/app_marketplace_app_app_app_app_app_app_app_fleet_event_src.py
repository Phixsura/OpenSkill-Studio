"""Fleet event sourcing — track event store metrics."""
from __future__ import annotations
def fleet_event_sourcing(stores: list[dict]) -> dict:
    total_events = sum(s.get("event_count", 0) for s in stores)
    total_snapshots = sum(s.get("snapshots", 0) for s in stores)
    avg_replay_ms = round(sum(s.get("replay_ms", 0) for s in stores) / max(len(stores), 1), 1)
    return {"stores": len(stores), "total_events": total_events,
            "snapshots": total_snapshots, "avg_replay_ms": avg_replay_ms, "fast": avg_replay_ms < 1000}
