"""Fleet Split.io — track experimentation platform metrics."""
from __future__ import annotations
def fleet_split_status(splits: list[dict]) -> dict:
    active = [s for s in splits if s.get("active", True)]
    with_metrics = [s for s in active if s.get("has_metrics", False)]
    treatments = sum(s.get("treatments", 0) for s in active)
    return {"total": len(splits), "active": len(active), "with_metrics": len(with_metrics),
            "treatments": treatments, "data_driven": len(with_metrics) == len(active)}
