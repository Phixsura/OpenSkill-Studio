"""Maintenance window — schedule and manage planned downtime."""

import secrets
from datetime import datetime, timedelta


def schedule_maintenance(*, app_id: str, title: str, start_time: str,
                           duration_min: int, affected: list[str]) -> dict:
    if duration_min < 5 or duration_min > 480:
        return {"error": "Duration must be 5-480 minutes"}
    if not affected:
        return {"error": "At least one affected component required"}
    end_time = (datetime.fromisoformat(start_time) + timedelta(minutes=duration_min)).isoformat()
    return {
        "window_id": f"mw_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "duration_min": duration_min,
        "affected_components": affected,
        "status": "scheduled",
        "notify_users": True,
    }


def get_upcoming_windows(*, windows: list[dict]) -> dict:
    now = datetime.utcnow().isoformat()
    upcoming = [w for w in windows if w.get("start_time", "") > now]
    active = [w for w in windows if w.get("start_time", "") <= now <= w.get("end_time", "")]
    return {
        "upcoming": sorted(upcoming, key=lambda w: w["start_time"]),
        "active": active,
        "total_upcoming": len(upcoming),
        "currently_in_maintenance": len(active) > 0,
    }
