"""Fleet AI Compliance Audit — track AI regulatory compliance status."""
from __future__ import annotations
def fleet_ai_compliance(audits: list[dict]) -> dict:
    passed = [a for a in audits if a.get("status") == "passed"]
    failed = [a for a in audits if a.get("status") == "failed"]
    frameworks = set()
    for a in audits:
        frameworks.update(a.get("frameworks", []))
    return {"audits": len(audits), "passed": len(passed), "failed": len(failed),
            "frameworks": sorted(frameworks), "compliant": len(failed) == 0}
