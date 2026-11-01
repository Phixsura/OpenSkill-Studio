"""Platform status page generator — generate public status page data."""
from __future__ import annotations


def generate_status_page(services: list[dict]) -> dict:
    operational = [s for s in services if s["status"] == "operational"]
    degraded = [s for s in services if s["status"] == "degraded"]
    outage = [s for s in services if s["status"] == "outage"]
    if outage:
        overall = "major_outage" if len(outage) > len(services) // 2 else "partial_outage"
    elif degraded:
        overall = "degraded_performance"
    else:
        overall = "all_systems_operational"
    groups: dict[str, list[dict]] = {}
    for s in services:
        g = s.get("group", "Other")
        groups.setdefault(g, []).append({"name": s["name"], "status": s["status"]})
    return {"overall": overall, "groups": groups,
            "operational": len(operational), "degraded": len(degraded),
            "outage": len(outage), "total": len(services)}


def uptime_bars(history: list[dict], days: int = 90) -> list[dict]:
    bars = []
    for day in history[-days:]:
        pct = day.get("uptime_pct", 100)
        color = "green" if pct >= 99.9 else ("yellow" if pct >= 99 else "red")
        bars.append({"date": day["date"], "uptime_pct": pct, "color": color})
    return bars
