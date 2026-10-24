"""Fleet Gatekeeper — track OPA Gatekeeper constraint enforcement."""
from __future__ import annotations
def fleet_gatekeeper_status(constraints: list[dict]) -> dict:
    enforced = [c for c in constraints if c.get("enforcement") == "deny"]
    violations = sum(c.get("violations", 0) for c in constraints)
    return {"total": len(constraints), "enforced": len(enforced),
            "audit_only": len(constraints) - len(enforced), "violations": violations,
            "clean": violations == 0}
