"""Fleet Replicate — track ML model hosting platform."""
from __future__ import annotations
def fleet_replicate_status(models: list[dict]) -> dict:
    active = [m for m in models if m.get("active", True)]
    predictions_24h = sum(m.get("predictions_24h", 0) for m in models)
    avg_run_time = round(sum(m.get("avg_run_sec", 0) for m in models) / max(len(models), 1), 1)
    return {"models": len(models), "active": len(active), "predictions_24h": predictions_24h,
            "avg_run_sec": avg_run_time, "all_active": len(active) == len(models)}
