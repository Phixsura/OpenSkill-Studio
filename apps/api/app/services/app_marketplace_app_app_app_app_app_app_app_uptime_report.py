"""Service uptime report generator — generate monthly uptime reports."""
from __future__ import annotations


def generate_report(services: list[dict], period: str = "October 2026") -> dict:
    total_uptime = 0
    reports = []
    for svc in services:
        uptime = svc.get("uptime_pct", 100)
        total_uptime += uptime
        incidents = svc.get("incidents", 0)
        downtime_min = svc.get("downtime_minutes", 0)
        sla_met = uptime >= svc.get("sla_target", 99.9)
        reports.append({"service": svc["name"], "uptime_pct": uptime,
                        "incidents": incidents, "downtime_minutes": downtime_min,
                        "sla_met": sla_met})
    avg_uptime = round(total_uptime / max(len(services), 1), 3)
    all_met = all(r["sla_met"] for r in reports)
    return {"period": period, "services": reports, "avg_uptime_pct": avg_uptime,
            "all_sla_met": all_met, "total_services": len(services)}
