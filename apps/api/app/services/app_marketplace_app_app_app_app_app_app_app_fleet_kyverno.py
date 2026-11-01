"""Fleet Kyverno — track policy engine enforcement."""
from __future__ import annotations
def fleet_kyverno_status(policies: list[dict]) -> dict:
    enforcing = [p for p in policies if p.get("mode") == "enforce"]
    audit = [p for p in policies if p.get("mode") == "audit"]
    violations = sum(p.get("violations", 0) for p in policies)
    return {"total": len(policies), "enforcing": len(enforcing), "audit": len(audit),
            "violations": violations, "compliant": violations == 0}
