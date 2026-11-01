"""Uptime monitor — 90-day uptime history with daily status."""

import html
from datetime import datetime, timezone


def build_uptime_monitor(*, daily_status: list[dict], service_name: str) -> dict:
    days = []
    up_days = 0
    for d in daily_status:
        status = d.get("status", "up")
        if status == "up":
            up_days += 1
        days.append({"date": d.get("date", ""), "status": status,
                      "color": {"up": "green", "degraded": "yellow", "down": "red"}.get(status, "gray")})
    total = len(days)
    uptime_pct = round(up_days / max(total, 1) * 100, 2)
    return {"service_name": html.escape(service_name), "days": days,
            "total_days": total, "up_days": up_days,
            "uptime_pct": uptime_pct,
            "nines": "99.99%" if uptime_pct >= 99.99 else f"{uptime_pct}%"}
