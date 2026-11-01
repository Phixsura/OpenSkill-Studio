"""Fleet SAST — static application security testing results."""
from __future__ import annotations
def fleet_sast_results(scans: list[dict]) -> dict:
    total_findings = sum(s.get("findings", 0) for s in scans)
    critical = sum(s.get("critical", 0) for s in scans)
    high = sum(s.get("high", 0) for s in scans)
    return {"scans": len(scans), "total_findings": total_findings,
            "critical": critical, "high": high,
            "secure": critical == 0 and high == 0}
