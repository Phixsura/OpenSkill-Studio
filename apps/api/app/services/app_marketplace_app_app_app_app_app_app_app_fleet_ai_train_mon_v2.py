"""Fleet AI Training Monitor v2 — track real-time training progress."""
from __future__ import annotations
def fleet_ai_training_monitor_v2(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    jobs_monitored = sum(m.get("jobs", 0) for m in monitors)
    metrics_tracked = sum(m.get("metrics", 0) for m in monitors)
    alerts_24h = sum(m.get("alerts_24h", 0) for m in monitors)
    return {"monitors": len(monitors), "active": len(active), "jobs": jobs_monitored,
            "metrics": metrics_tracked, "alerts_24h": alerts_24h, "observing": jobs_monitored > 0}
