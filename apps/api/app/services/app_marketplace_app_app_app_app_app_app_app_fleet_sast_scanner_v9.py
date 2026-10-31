"""Fleet SAST Scanner v9 — track static application security testing."""
from __future__ import annotations
def fleet_sast_scanner_v9(scans: list[dict]) -> dict:
    findings = sum(s.get("findings", 0) for s in scans)
    critical = sum(s.get("critical", 0) for s in scans)
    fixed = sum(s.get("fixed", 0) for s in scans)
    return {"scans": len(scans), "findings": findings, "critical": critical,
            "fixed": fixed, "healthy": critical == 0}
