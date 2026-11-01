"""Fleet change velocity — track deployment velocity metrics."""
from __future__ import annotations
def fleet_change_velocity(window: dict) -> dict:
    deploys = window.get("deploys", 0)
    hours = window.get("hours", 24)
    rate = round(deploys / max(hours, 1), 2)
    return {"deploys": deploys, "hours": hours, "rate_per_hour": rate,
            "high_velocity": rate > 2}
