"""Fleet Onboarding v9 — track developer onboarding pipeline."""
from __future__ import annotations
def fleet_onboarding_v9(devs: list[dict]) -> dict:
    completed = [d for d in devs if d.get("onboarded")]
    in_progress = [d for d in devs if not d.get("onboarded")]
    avg_days = sum(d.get("days_to_productive", 0) for d in devs if d.get("onboarded")) / len(completed) if completed else 0
    return {"total": len(devs), "completed": len(completed), "in_progress": len(in_progress),
            "avg_days_to_productive": round(avg_days, 1), "healthy": avg_days < 14}
