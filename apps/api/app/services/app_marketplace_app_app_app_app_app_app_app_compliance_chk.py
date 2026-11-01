"""Compliance checker — verify app compliance with policies."""
from __future__ import annotations

POLICIES = {
    "gdpr": {"name": "GDPR", "checks": ["data_processing_agreement", "consent_mechanism",
              "right_to_deletion", "data_portability", "privacy_policy"]},
    "soc2": {"name": "SOC 2", "checks": ["encryption_at_rest", "encryption_in_transit",
              "access_controls", "audit_logging", "incident_response"]},
    "hipaa": {"name": "HIPAA", "checks": ["phi_encryption", "access_controls",
               "audit_trail", "baa_signed", "minimum_necessary"]},
}


def check_compliance(policy_id: str, completed: list[str]) -> dict:
    policy = POLICIES.get(policy_id)
    if not policy:
        return {"valid": False, "error": "unknown_policy"}
    checks = policy["checks"]
    results = []
    for c in checks:
        passed = c in completed
        results.append({"check": c, "passed": passed})
    passed_count = sum(1 for r in results if r["passed"])
    pct = round(passed_count / len(checks) * 100)
    return {"policy": policy["name"], "checks": results,
            "passed": passed_count, "total": len(checks),
            "compliant": passed_count == len(checks),
            "compliance_pct": pct}


def audit_all(completed: dict[str, list[str]]) -> dict:
    results = {}
    compliant_count = 0
    for pid in POLICIES:
        r = check_compliance(pid, completed.get(pid, []))
        results[pid] = r
        if r.get("compliant"):
            compliant_count += 1
    return {"policies": results, "total": len(POLICIES),
            "compliant": compliant_count,
            "overall": compliant_count == len(POLICIES)}
