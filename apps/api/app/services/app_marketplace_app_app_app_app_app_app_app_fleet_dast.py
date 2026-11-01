"""Fleet DAST — dynamic application security testing results."""
from __future__ import annotations
def fleet_dast_results(scans: list[dict]) -> dict:
    total_vulns = sum(s.get("vulnerabilities", 0) for s in scans)
    critical = sum(s.get("critical", 0) for s in scans)
    return {"scans": len(scans), "total_vulns": total_vulns,
            "critical": critical, "secure": critical == 0}
