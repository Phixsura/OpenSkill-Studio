"""Fleet SLO Budget v9 — track error budget consumption and SLO compliance."""
from __future__ import annotations
def fleet_slo_budget_v9(slos: list[dict]) -> dict:
    compliant = [s for s in slos if s.get("budget_remaining_pct", 100) > 0]
    burned = [s for s in slos if s.get("budget_remaining_pct", 100) <= 0]
    avg_remaining = sum(s.get("budget_remaining_pct", 100) for s in slos) / len(slos) if slos else 0
    return {"total_slos": len(slos), "compliant": len(compliant), "burned": len(burned),
            "avg_budget_remaining": round(avg_remaining, 1), "healthy": len(burned) == 0}
