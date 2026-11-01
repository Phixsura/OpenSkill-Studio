"""Fleet SLO Compliance v9 — track SLO compliance across all services."""
from __future__ import annotations
def fleet_slo_compliance_v9(slos: list[dict]) -> dict:
    met = [s for s in slos if s.get("met")]
    at_risk = [s for s in slos if s.get("at_risk")]
    breached = [s for s in slos if s.get("breached")]
    avg_attainment = sum(s.get("attainment_pct", 0) for s in slos) / len(slos) if slos else 0
    return {"slos": len(slos), "met": len(met), "at_risk": len(at_risk), "breached": len(breached),
            "avg_attainment": round(avg_attainment, 1), "healthy": len(breached) == 0}
