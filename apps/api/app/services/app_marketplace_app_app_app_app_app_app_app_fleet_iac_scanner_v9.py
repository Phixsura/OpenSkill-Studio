"""Fleet IaC Scanner v9 — track Infrastructure as Code security scanning."""
from __future__ import annotations
def fleet_iac_scanner_v9(scans: list[dict]) -> dict:
    passed = [s for s in scans if s.get("passed")]
    misconfigs = sum(s.get("misconfigurations", 0) for s in scans)
    critical = sum(s.get("critical", 0) for s in scans)
    return {"scans": len(scans), "passed": len(passed), "misconfigurations": misconfigs,
            "critical": critical, "healthy": critical == 0}
