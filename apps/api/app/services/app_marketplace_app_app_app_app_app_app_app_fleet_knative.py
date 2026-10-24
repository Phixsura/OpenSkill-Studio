"""Fleet Knative — track serverless function health."""
from __future__ import annotations
def fleet_knative_status(services: list[dict]) -> dict:
    ready = [s for s in services if s.get("ready", True)]
    cold_starts = sum(s.get("cold_starts_24h", 0) for s in services)
    avg_latency = round(sum(s.get("avg_latency_ms", 0) for s in services) / max(len(services), 1), 1)
    return {"total": len(services), "ready": len(ready), "cold_starts_24h": cold_starts,
            "avg_latency_ms": avg_latency, "all_ready": len(ready) == len(services)}
