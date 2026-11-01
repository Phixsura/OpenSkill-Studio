"""Fleet Observability Hub v9 — unified metrics, logs, and traces dashboard."""
from __future__ import annotations
def fleet_observability_hub_v9(sources: list[dict]) -> dict:
    connected = [s for s in sources if s.get("connected")]
    metrics_sec = sum(s.get("metrics_per_sec", 0) for s in sources)
    logs_sec = sum(s.get("logs_per_sec", 0) for s in sources)
    return {"sources": len(sources), "connected": len(connected), "metrics_per_sec": metrics_sec,
            "logs_per_sec": logs_sec, "healthy": len(connected) == len(sources)}
