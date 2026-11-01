"""Fleet AI Model Lineage v2 — track model training provenance chain."""
from __future__ import annotations
def fleet_ai_model_lineage_v2(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    models = sum(t.get("models", 0) for t in trackers)
    lineage_depth = max((t.get("depth", 0) for t in trackers), default=0)
    datasets_linked = sum(t.get("datasets", 0) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "models": models,
            "depth": lineage_depth, "datasets": datasets_linked, "traceable": lineage_depth > 0}
