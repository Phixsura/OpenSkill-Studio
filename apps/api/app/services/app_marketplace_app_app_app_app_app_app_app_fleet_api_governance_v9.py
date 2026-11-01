"""Fleet API Governance v9 — track API design governance and standards."""
from __future__ import annotations
def fleet_api_governance_v9(apis: list[dict]) -> dict:
    compliant = [a for a in apis if a.get("governance_compliant")]
    reviewed = [a for a in apis if a.get("design_reviewed")]
    standards = len({a.get("standard") for a in apis if a.get("standard")})
    return {"apis": len(apis), "compliant": len(compliant), "reviewed": len(reviewed),
            "standards_applied": standards, "healthy": len(compliant) == len(apis)}
