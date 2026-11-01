"""Deployment window scheduler — manage maintenance/deployment windows."""
from __future__ import annotations


def create_window(name: str, day_of_week: int, start_hour: int, duration_hours: int,
                  timezone: str = "UTC") -> dict:
    end_hour = (start_hour + duration_hours) % 24
    return {"name": name, "day_of_week": day_of_week, "start_hour": start_hour,
            "end_hour": end_hour, "duration_hours": duration_hours,
            "timezone": timezone}


def is_in_window(current_day: int, current_hour: int, window: dict) -> dict:
    day_match = current_day == window["day_of_week"]
    start = window["start_hour"]
    end = start + window["duration_hours"]
    if end <= 24:
        hour_match = start <= current_hour < end
    else:
        hour_match = current_hour >= start or current_hour < end % 24
    in_window = day_match and hour_match
    return {"in_window": in_window, "window": window["name"],
            "remaining_hours": max(0, end - current_hour) if in_window else 0}


def next_window(windows: list[dict], current_day: int, current_hour: int) -> dict | None:
    best = None
    best_delta = float("inf")
    for w in windows:
        day_delta = (w["day_of_week"] - current_day) % 7
        if day_delta == 0 and w["start_hour"] <= current_hour:
            day_delta = 7
        hour_delta = day_delta * 24 + (w["start_hour"] - current_hour)
        if hour_delta < best_delta:
            best_delta = hour_delta
            best = {**w, "hours_until": hour_delta}
    return best
