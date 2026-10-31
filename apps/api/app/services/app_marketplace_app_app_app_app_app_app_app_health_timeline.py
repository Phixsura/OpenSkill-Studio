"""Service health timeline — historical health status over time."""
from __future__ import annotations


def build_timeline(entries: list[dict], window_hours: int = 24) -> dict:
    timeline = []
    uptime_slots = 0
    total_slots = 0
    for e in entries:
        status = e.get("status", "unknown")
        is_up = status in ("healthy", "operational")
        total_slots += 1
        if is_up:
            uptime_slots += 1
        timeline.append({"timestamp": e.get("timestamp", 0), "status": status, "healthy": is_up})
    uptime_pct = round(uptime_slots / max(total_slots, 1) * 100, 2)
    incidents = sum(1 for i, e in enumerate(timeline) if not e["healthy"] and (i == 0 or timeline[i-1]["healthy"]))
    return {"timeline": timeline, "window_hours": window_hours,
            "total_checks": total_slots, "uptime_pct": uptime_pct,
            "incidents": incidents}


def compare_periods(current: dict, previous: dict) -> dict:
    delta = round(current["uptime_pct"] - previous["uptime_pct"], 2)
    return {"current_uptime": current["uptime_pct"], "previous_uptime": previous["uptime_pct"],
            "delta": delta, "improving": delta > 0,
            "incident_delta": current["incidents"] - previous["incidents"]}
