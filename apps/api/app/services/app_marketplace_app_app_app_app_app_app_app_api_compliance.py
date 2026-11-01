"""API compliance checker — verify APIs comply with organizational standards."""
from __future__ import annotations


def check_compliance(endpoint: dict, standards: dict) -> dict:
    issues = []
    # Check naming convention
    path = endpoint.get("path", "")
    if standards.get("snake_case_paths") and any(c.isupper() for c in path):
        issues.append({"rule": "snake_case_paths", "severity": "warning"})
    # Check versioning
    if standards.get("require_versioning") and "/v" not in path:
        issues.append({"rule": "require_versioning", "severity": "error"})
    # Check auth
    if standards.get("require_auth") and not endpoint.get("auth_required"):
        issues.append({"rule": "require_auth", "severity": "error"})
    # Check response format
    if standards.get("require_envelope") and not endpoint.get("uses_envelope"):
        issues.append({"rule": "require_envelope", "severity": "warning"})
    compliant = not any(i["severity"] == "error" for i in issues)
    return {"endpoint": path, "compliant": compliant, "issues": issues,
            "issue_count": len(issues)}


def fleet_compliance(endpoints: list[dict], standards: dict) -> dict:
    results = [check_compliance(ep, standards) for ep in endpoints]
    compliant = sum(1 for r in results if r["compliant"])
    return {"total": len(results), "compliant": compliant,
            "non_compliant": len(results) - compliant,
            "compliance_pct": round(compliant / max(len(results), 1) * 100, 1)}
