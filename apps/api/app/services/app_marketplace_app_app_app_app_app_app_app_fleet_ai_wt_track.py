"""Fleet AI Weight Tracker — track model weight evolution over training."""
from __future__ import annotations
def fleet_ai_weight_tracker(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    models_tracked = sum(t.get("models", 0) for t in trackers)
    checkpoints = sum(t.get("checkpoints", 0) for t in trackers)
    drift_detected = sum(t.get("drift_events", 0) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "models": models_tracked,
            "checkpoints": checkpoints, "drift_events": drift_detected, "tracking": models_tracked > 0}
