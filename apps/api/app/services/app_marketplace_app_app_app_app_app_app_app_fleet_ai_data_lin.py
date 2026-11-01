"""Fleet AI Data Lineage — track data provenance and transformation history."""
from __future__ import annotations
def fleet_ai_data_lineage(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    datasets_tracked = sum(t.get("datasets", 0) for t in trackers)
    transformations = sum(t.get("transforms", 0) for t in trackers)
    depth = max((t.get("max_depth", 0) for t in trackers), default=0)
    return {"trackers": len(trackers), "active": len(active), "datasets": datasets_tracked,
            "transforms": transformations, "max_depth": depth, "traceable": depth > 0}
