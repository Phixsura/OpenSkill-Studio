"""Fleet Compliance Scanner v9 — track regulatory compliance checks."""
from __future__ import annotations
def fleet_compliance_scanner_v9(checks: list[dict]) -> dict:
    passed = [c for c in checks if c.get("passed")]
    failed = [c for c in checks if not c.get("passed")]
    frameworks = len({c.get("framework") for c in checks if c.get("framework")})
    return {"total_checks": len(checks), "passed": len(passed), "failed": len(failed),
            "frameworks": frameworks, "healthy": len(failed) == 0}
