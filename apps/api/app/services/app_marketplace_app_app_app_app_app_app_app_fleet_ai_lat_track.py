"""Fleet AI Latency Tracker — track AI endpoint latency percentiles."""
from __future__ import annotations
def fleet_ai_latency_tracker(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    endpoints = sum(t.get("endpoints", 0) for t in trackers)
    p50_ms = round(sum(t.get("p50_ms", 0) for t in trackers) / max(len(trackers), 1), 1)
    p99_ms = round(sum(t.get("p99_ms", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "endpoints": endpoints,
            "p50_ms": p50_ms, "p99_ms": p99_ms, "fast": p99_ms < 200}
