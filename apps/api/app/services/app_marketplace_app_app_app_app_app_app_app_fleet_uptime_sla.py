"""Fleet uptime SLA — calculate platform-wide uptime."""
from __future__ import annotations
def fleet_uptime_sla(window: dict) -> dict:
    total_min = window.get("total_minutes", 43200)
    downtime_min = window.get("downtime_minutes", 0)
    uptime_pct = round((total_min - downtime_min) / total_min * 100, 4)
    nines = 0
    u = uptime_pct
    while u >= 90 and nines < 6:
        nines += 1
        u = (u - 90) * 10 + 90 if u < 100 else 100
        if u >= 100: break
    return {"uptime_pct": uptime_pct, "downtime_min": downtime_min,
            "nines": nines, "meets_sla": uptime_pct >= 99.9}
