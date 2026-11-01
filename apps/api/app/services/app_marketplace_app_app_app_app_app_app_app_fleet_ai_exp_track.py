"""Fleet AI Experiment Tracker — track ML experiment runs and metrics."""
from __future__ import annotations
def fleet_ai_experiment_tracker(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    experiments = sum(t.get("experiments", 0) for t in trackers)
    runs = sum(t.get("runs", 0) for t in trackers)
    best_metric = max((t.get("best_metric", 0) for t in trackers), default=0)
    return {"trackers": len(trackers), "active": len(active), "experiments": experiments,
            "runs": runs, "best_metric": best_metric}
