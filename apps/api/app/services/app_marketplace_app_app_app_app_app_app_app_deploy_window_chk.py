"""Deployment window checker — verify current time is within deploy window."""
from __future__ import annotations


def is_deploy_allowed(current_hour: int, current_day: int, windows: list[dict],
                       freeze_active: bool = False) -> dict:
    if freeze_active:
        return {"allowed": False, "reason": "deploy_freeze_active"}
    for w in windows:
        if current_day in w.get("days", []) or not w.get("days"):
            start = w.get("start_hour", 0)
            end = w.get("end_hour", 24)
            if start <= current_hour < end:
                return {"allowed": True, "window": w.get("name", ""),
                        "remaining_hours": end - current_hour}
    return {"allowed": False, "reason": "outside_deploy_window"}


def next_deploy_window(current_hour: int, current_day: int, windows: list[dict]) -> dict:
    for w in windows:
        start = w.get("start_hour", 0)
        days = w.get("days", list(range(7)))
        if current_day in days and current_hour < start:
            return {"window": w["name"], "hours_until": start - current_hour}
        for d in range(1, 8):
            next_day = (current_day + d) % 7
            if next_day in days:
                hours = (24 - current_hour) + (d - 1) * 24 + start
                return {"window": w["name"], "hours_until": hours}
    return {"window": "none", "hours_until": -1}
