"""Maintenance window — scheduled maintenance management."""

import html
from datetime import datetime, timezone, timedelta


def create_maintenance(*, title: str, start: str, duration_min: int = 60,
                         services: list[str] | None = None) -> dict:
    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_dt = start_dt + timedelta(minutes=duration_min)
    now = datetime.now(timezone.utc)
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    status = "scheduled" if start_dt > now else "in_progress" if end_dt > now else "completed"
    return {"title": html.escape(title), "start": start_dt.isoformat(),
            "end": end_dt.isoformat(), "duration_min": duration_min,
            "services": services or ["all"], "status": status}


def build_maintenance_schedule(*, windows: list[dict]) -> dict:
    upcoming = [w for w in windows if w.get("status") == "scheduled"]
    active = [w for w in windows if w.get("status") == "in_progress"]
    return {"windows": windows, "total": len(windows),
            "upcoming": len(upcoming), "active": len(active),
            "has_active": len(active) > 0}
