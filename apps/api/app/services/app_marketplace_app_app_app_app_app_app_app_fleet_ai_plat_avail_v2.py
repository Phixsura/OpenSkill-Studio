"""Fleet AI Platform Availability v2 — track five-nines availability."""
from __future__ import annotations
def fleet_ai_platform_availability_v2(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    uptime = round(sum(m.get("uptime_pct", 0) for m in monitors) / max(len(monitors), 1), 4)
    downtime_min = round(sum(m.get("downtime_min", 0) for m in monitors) / max(len(monitors), 1), 1)
    nines = 5 if uptime >= 99.999 else (4 if uptime >= 99.99 else 3)
    return {"monitors": len(monitors), "active": len(active), "uptime": uptime,
            "downtime_min": downtime_min, "nines": nines, "five_nines": nines >= 5}
