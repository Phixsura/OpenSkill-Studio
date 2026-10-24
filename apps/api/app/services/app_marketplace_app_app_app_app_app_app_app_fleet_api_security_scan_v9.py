"""Fleet API Security Scan v9 — track API security vulnerability scanning."""
from __future__ import annotations
def fleet_api_security_scan_v9(scans: list[dict]) -> dict:
    passed = [s for s in scans if s.get("passed")]
    owasp_top10 = sum(s.get("owasp_findings", 0) for s in scans)
    auth_issues = sum(s.get("auth_issues", 0) for s in scans)
    return {"scans": len(scans), "passed": len(passed), "owasp_findings": owasp_top10,
            "auth_issues": auth_issues, "healthy": owasp_top10 == 0 and auth_issues == 0}
