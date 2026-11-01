"""Fleet Trivy — track container security scanning."""
from __future__ import annotations
def fleet_trivy_status(scans: list[dict]) -> dict:
    clean = [s for s in scans if s.get("critical", 0) == 0 and s.get("high", 0) == 0]
    total_critical = sum(s.get("critical", 0) for s in scans)
    total_high = sum(s.get("high", 0) for s in scans)
    return {"total_scans": len(scans), "clean": len(clean), "critical": total_critical,
            "high": total_high, "all_clean": len(clean) == len(scans)}
