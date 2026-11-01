"""Fleet AI Early Stopping — track training early termination."""
from __future__ import annotations
def fleet_ai_early_stopping(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    jobs = sum(m.get("jobs", 0) for m in managers)
    stopped_early = sum(m.get("stopped", 0) for m in managers)
    compute_saved_pct = round(sum(m.get("saved_pct", 0) for m in managers) / max(len(managers), 1), 1)
    return {"managers": len(managers), "active": len(active), "jobs": jobs,
            "stopped": stopped_early, "saved_pct": compute_saved_pct, "efficient": compute_saved_pct > 10}
