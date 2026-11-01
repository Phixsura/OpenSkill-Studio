"""Fleet DAST Scanner v9 — track dynamic application security testing."""
from __future__ import annotations
def fleet_dast_scanner_v9(scans: list[dict]) -> dict:
    completed = [s for s in scans if s.get("completed")]
    vulns_found = sum(s.get("vulnerabilities", 0) for s in scans)
    avg_duration = sum(s.get("duration_min", 0) for s in scans) / len(scans) if scans else 0
    return {"scans": len(scans), "completed": len(completed), "vulnerabilities": vulns_found,
            "avg_duration_min": round(avg_duration, 1), "healthy": vulns_found == 0}
