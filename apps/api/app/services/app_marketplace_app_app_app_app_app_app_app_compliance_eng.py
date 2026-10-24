"""Compliance policy engine — evaluate resources against compliance policies."""
from __future__ import annotations


def evaluate_policy(resource: dict, policies: list[dict]) -> dict:
    violations = []
    for policy in policies:
        field = policy["field"]
        actual = resource.get(field)
        rule = policy["rule"]
        if rule == "required" and not actual:
            violations.append({"policy": policy["name"], "field": field, "rule": rule, "severity": policy.get("severity", "warning")})
        elif rule == "min_length" and isinstance(actual, str) and len(actual) < policy.get("value", 0):
            violations.append({"policy": policy["name"], "field": field, "rule": rule, "severity": policy.get("severity", "warning")})
        elif rule == "one_of" and actual not in policy.get("values", []):
            violations.append({"policy": policy["name"], "field": field, "rule": rule, "severity": policy.get("severity", "warning")})
    compliant = len(violations) == 0
    critical = sum(1 for v in violations if v["severity"] == "critical")
    return {"compliant": compliant, "violations": violations,
            "total_policies": len(policies), "critical_violations": critical}


def compliance_score(resources: list[dict]) -> dict:
    total = len(resources)
    compliant = sum(1 for r in resources if r.get("compliant"))
    score = round(compliant / max(total, 1) * 100, 1)
    return {"score": score, "compliant": compliant, "non_compliant": total - compliant, "total": total}
