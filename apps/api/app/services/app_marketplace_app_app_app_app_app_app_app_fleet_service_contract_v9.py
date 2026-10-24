"""Fleet Service Contract v9 — track service-level contract compliance."""
from __future__ import annotations
def fleet_service_contract_v9(contracts: list[dict]) -> dict:
    compliant = [c for c in contracts if c.get("compliant")]
    sla_met = [c for c in contracts if c.get("sla_met")]
    penalties = sum(c.get("penalty_amount", 0) for c in contracts)
    return {"contracts": len(contracts), "compliant": len(compliant), "sla_met": len(sla_met),
            "penalties": round(penalties, 2), "healthy": len(compliant) == len(contracts)}
