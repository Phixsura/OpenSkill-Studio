"""Deployment window scheduler — define safe deployment windows."""
from __future__ import annotations


WINDOWS = {
    "business_hours": {"start_hour": 9, "end_hour": 17, "days": [0, 1, 2, 3, 4]},
    "off_peak": {"start_hour": 22, "end_hour": 6, "days": [0, 1, 2, 3, 4, 5, 6]},
    "weekend": {"start_hour": 8, "end_hour": 20, "days": [5, 6]},
}


def check_deploy_window(window_name: str, current_hour: int, current_day: int) -> dict:
    window = WINDOWS.get(window_name)
    if not window:
        return {"allowed": False, "error": "unknown_window"}
    in_hours = (window["start_hour"] <= current_hour < window["end_hour"]) if window["start_hour"] < window["end_hour"] else (current_hour >= window["start_hour"] or current_hour < window["end_hour"])
    in_day = current_day in window["days"]
    allowed = in_hours and in_day
    return {"allowed": allowed, "window": window_name, "current_hour": current_hour,
            "current_day": current_day, "reason": "" if allowed else "outside_window"}


def next_available_window(windows: list[str], current_hour: int, current_day: int) -> dict:
    for w in windows:
        r = check_deploy_window(w, current_hour, current_day)
        if r.get("allowed"):
            return {"window": w, "available_now": True}
    return {"window": None, "available_now": False, "suggestion": "Wait for next deployment window"}
