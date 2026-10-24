"""Service uptime calculator — precise uptime calculations."""
from __future__ import annotations


def calculate_uptime(total_seconds: int, downtime_seconds: int) -> dict:
    uptime_seconds = total_seconds - downtime_seconds
    uptime_pct = round(uptime_seconds / max(total_seconds, 1) * 100, 4)
    nines = 0
    pct = uptime_pct
    while pct >= 90 and nines < 6:
        nines += 1
        pct = (pct - 90) * 10
    downtime_per_month = round(downtime_seconds / max(total_seconds, 1) * 30 * 24 * 3600)
    downtime_per_year = round(downtime_seconds / max(total_seconds, 1) * 365 * 24 * 3600)
    return {"uptime_pct": uptime_pct, "nines": nines,
            "downtime_month_sec": downtime_per_month,
            "downtime_year_sec": downtime_per_year,
            "display": f"{uptime_pct}% ({nines} nines)"}


def compare_uptime(current: dict, target_pct: float) -> dict:
    met = current["uptime_pct"] >= target_pct
    margin = round(current["uptime_pct"] - target_pct, 4)
    return {"target": target_pct, "actual": current["uptime_pct"],
            "met": met, "margin": margin,
            "status": "met" if met else "breached"}
