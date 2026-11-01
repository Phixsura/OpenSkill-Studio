"""Fleet AI Loss Tracker — track training loss curves and convergence."""
from __future__ import annotations
def fleet_ai_loss_tracker(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    jobs_tracked = sum(t.get("jobs", 0) for t in trackers)
    current_loss = round(sum(t.get("loss", 0) for t in trackers) / max(len(trackers), 1), 4)
    converged = sum(1 for t in trackers if t.get("converged", False))
    return {"trackers": len(trackers), "active": len(active), "jobs": jobs_tracked,
            "loss": current_loss, "converged": converged, "training": jobs_tracked > 0}
