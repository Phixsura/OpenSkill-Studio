"""Fleet AI DataOps v8 — track ultimate data operations."""
from __future__ import annotations
def fleet_ai_dataops_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    pipelines = sum(s.get("pipelines", 0) for s in systems)
    datasets = sum(s.get("datasets", 0) for s in systems)
    quality = round(sum(s.get("quality_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "pipelines": pipelines,
            "datasets": datasets, "quality": quality, "high_quality": quality > 95}
