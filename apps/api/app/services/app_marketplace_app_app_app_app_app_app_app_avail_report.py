"""Service availability reporter — generate availability reports."""
from __future__ import annotations


def generate_availability_report(services: list[dict], period_days: int = 30) -> dict:
    results = []
    total_uptime = 0
    for s in services:
        uptime = s.get("uptime_pct", 100)
        downtime_min = round((100 - uptime) / 100 * period_days * 24 * 60, 1)
        sla_met = uptime >= s.get("sla_target", 99.9)
        results.append({"name": s["name"], "uptime_pct": uptime,
                         "downtime_min": downtime_min, "sla_target": s.get("sla_target", 99.9),
                         "sla_met": sla_met, "incidents": s.get("incidents", 0)})
        total_uptime += uptime
    avg_uptime = round(total_uptime / max(len(services), 1), 3)
    sla_breaches = sum(1 for r in results if not r["sla_met"])
    return {"services": results, "period_days": period_days,
            "avg_uptime": avg_uptime, "sla_breaches": sla_breaches,
            "all_sla_met": sla_breaches == 0}
