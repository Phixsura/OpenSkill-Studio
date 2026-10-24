"""Fleet Log Pipeline v9 — track log ingestion and processing rates."""
from __future__ import annotations
def fleet_log_pipeline_v9(pipelines: list[dict]) -> dict:
    ingested = sum(p.get("events_per_sec", 0) for p in pipelines)
    dropped = sum(p.get("dropped", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "ingestion_rate": ingested, "dropped": dropped,
            "drop_rate_pct": round(dropped / (ingested + dropped) * 100, 2) if (ingested + dropped) else 0,
            "healthy": dropped == 0}
