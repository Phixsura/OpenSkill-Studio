"""Fleet Metric Pipeline v9 — track metrics collection and aggregation."""
from __future__ import annotations
def fleet_metric_pipeline_v9(collectors: list[dict]) -> dict:
    active = [c for c in collectors if c.get("active")]
    metrics_sec = sum(c.get("metrics_per_sec", 0) for c in collectors)
    cardinality = sum(c.get("cardinality", 0) for c in collectors)
    return {"collectors": len(collectors), "active": len(active), "metrics_per_sec": metrics_sec,
            "total_cardinality": cardinality, "healthy": len(active) == len(collectors)}
