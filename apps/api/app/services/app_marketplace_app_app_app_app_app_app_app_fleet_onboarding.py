"""Fleet developer onboarding — track onboarding metrics."""
from __future__ import annotations
def fleet_dev_onboarding(devs: list[dict]) -> dict:
    completed = [d for d in devs if d.get("onboarded", False)]
    avg_days = round(sum(d.get("onboard_days", 0) for d in completed) / max(len(completed), 1), 1)
    return {"total": len(devs), "onboarded": len(completed), "pending": len(devs) - len(completed),
            "avg_days": avg_days, "fast": avg_days <= 5}
