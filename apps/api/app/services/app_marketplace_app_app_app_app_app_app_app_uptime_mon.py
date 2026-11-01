"""Uptime monitor — track service uptime and availability."""
from __future__ import annotations


def calculate_uptime(checks: list[dict]) -> dict:
    total = len(checks)
    up = sum(1 for c in checks if c.get("status") == "up")
    down_periods = []
    for c in checks:
        if c.get("status") == "down":
            down_periods.append({"timestamp": c.get("timestamp", ""), "duration_sec": c.get("duration_sec", 0)})
    uptime_pct = round(up / max(total, 1) * 100, 3)
    total_downtime = sum(d["duration_sec"] for d in down_periods)
    return {"total_checks": total, "up": up, "down": total - up,
            "uptime_pct": uptime_pct, "total_downtime_sec": total_downtime,
            "down_periods": down_periods,
            "sla_met": uptime_pct >= 99.9}


def uptime_summary(monitors: list[dict]) -> dict:
    all_met = all(m.get("sla_met", False) for m in monitors)
    avg_uptime = round(sum(m.get("uptime_pct", 0) for m in monitors) / max(len(monitors), 1), 3)
    worst = min(monitors, key=lambda m: m.get("uptime_pct", 100)) if monitors else None
    return {"monitor_count": len(monitors), "avg_uptime": avg_uptime,
            "all_sla_met": all_met,
            "worst_service": worst.get("name", "") if worst else None}
