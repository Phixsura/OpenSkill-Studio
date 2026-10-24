"""Uptime calculator — calculate service uptime from incident data."""
from __future__ import annotations


def calculate_uptime(total_minutes: int, downtime_minutes: int) -> dict:
    uptime_minutes = total_minutes - downtime_minutes
    uptime_pct = round(uptime_minutes / max(total_minutes, 1) * 100, 4)
    nines = 0
    if uptime_pct >= 99.999:
        nines = 5
    elif uptime_pct >= 99.99:
        nines = 4
    elif uptime_pct >= 99.9:
        nines = 3
    elif uptime_pct >= 99:
        nines = 2
    return {"uptime_pct": uptime_pct, "downtime_minutes": downtime_minutes,
            "total_minutes": total_minutes, "nines": nines,
            "sla_label": f"{nines}-nines" if nines >= 2 else "below-SLA"}


def monthly_report(incidents: list[dict], total_minutes: int = 43200) -> dict:
    total_down = sum(i.get("duration_minutes", 0) for i in incidents)
    uptime = calculate_uptime(total_minutes, total_down)
    return {"incidents": len(incidents), "total_downtime_minutes": total_down,
            **uptime}
