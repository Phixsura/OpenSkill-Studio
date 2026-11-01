"""Service level report — comprehensive SLO/SLI/SLA report for executives."""
from __future__ import annotations


def generate_service_level_report(services: list[dict], period: str) -> dict:
    total = len(services)
    slo_met = sum(1 for s in services if s.get("slo_met"))
    avg_uptime = round(sum(s.get("uptime_pct", 100) for s in services) / max(total, 1), 3)
    avg_error = round(sum(s.get("error_rate_pct", 0) for s in services) / max(total, 1), 3)
    total_incidents = sum(s.get("incidents", 0) for s in services)
    total_downtime = sum(s.get("downtime_min", 0) for s in services)
    executive_summary = "All SLOs met" if slo_met == total else f"{total - slo_met} SLO breaches"
    return {"period": period, "total_services": total, "slo_met": slo_met,
            "slo_breached": total - slo_met, "avg_uptime_pct": avg_uptime,
            "avg_error_rate_pct": avg_error, "total_incidents": total_incidents,
            "total_downtime_min": total_downtime, "executive_summary": executive_summary,
            "compliance_pct": round(slo_met / max(total, 1) * 100, 1)}
