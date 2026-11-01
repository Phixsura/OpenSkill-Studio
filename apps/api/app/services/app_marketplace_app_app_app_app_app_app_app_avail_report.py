"""Availability report — generate comprehensive availability reports."""
from __future__ import annotations


def generate_availability_report(services: list[dict], period: str) -> dict:
    total_uptime = sum(s.get("uptime_pct", 100) for s in services)
    avg_uptime = round(total_uptime / max(len(services), 1), 3)
    total_downtime = sum(s.get("downtime_minutes", 0) for s in services)
    incidents = sum(s.get("incidents", 0) for s in services)
    sla_breaches = sum(1 for s in services if s.get("uptime_pct", 100) < s.get("sla_target", 99.9))
    by_service = [{"service": s["name"], "uptime_pct": s.get("uptime_pct", 100),
                    "downtime_min": s.get("downtime_minutes", 0),
                    "sla_met": s.get("uptime_pct", 100) >= s.get("sla_target", 99.9)}
                   for s in sorted(services, key=lambda x: x.get("uptime_pct", 100))]
    return {"period": period, "avg_uptime_pct": avg_uptime,
            "total_downtime_minutes": total_downtime, "total_incidents": incidents,
            "sla_breaches": sla_breaches, "services": by_service,
            "all_sla_met": sla_breaches == 0}
