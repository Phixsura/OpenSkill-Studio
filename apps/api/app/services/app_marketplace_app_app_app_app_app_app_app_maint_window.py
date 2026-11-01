"""Maintenance window scheduler — plan and track downtime windows."""
from __future__ import annotations
import time


def create_window(title: str, start_ts: float, duration_min: int,
                  affected: list[str], notify: bool = True) -> dict:
    return {"title": title, "start_ts": start_ts, "end_ts": start_ts + duration_min * 60,
            "duration_min": duration_min, "affected_services": affected,
            "notify": notify, "status": "scheduled"}


def check_active(windows: list[dict], now: float | None = None) -> dict:
    now = now or time.time()
    active = [w for w in windows if w["start_ts"] <= now <= w["end_ts"]]
    upcoming = [w for w in windows if w["start_ts"] > now]
    completed = [w for w in windows if w["end_ts"] < now]
    return {"active": active, "active_count": len(active),
            "upcoming": len(upcoming), "completed": len(completed),
            "in_maintenance": len(active) > 0}


def affected_services(windows: list[dict]) -> list[str]:
    services = set()
    for w in windows:
        if w.get("status") != "cancelled":
            services.update(w.get("affected_services", []))
    return sorted(services)
