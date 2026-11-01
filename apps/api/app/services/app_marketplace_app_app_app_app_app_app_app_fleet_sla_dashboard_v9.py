"""Fleet SLA Dashboard v9 — track SLA compliance across all services."""
from __future__ import annotations
def fleet_sla_dashboard_v9(services: list[dict]) -> dict:
    compliant = [s for s in services if s.get("sla_met", True)]
    breached = [s for s in services if not s.get("sla_met", True)]
    avg_uptime = sum(s.get("uptime_pct", 99.9) for s in services) / len(services) if services else 0
    return {"services": len(services), "compliant": len(compliant), "breached": len(breached),
            "avg_uptime_pct": round(avg_uptime, 3), "healthy": len(breached) == 0}
