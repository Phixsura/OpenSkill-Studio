"""Platform governance policy — enforce organizational standards."""
from __future__ import annotations

POLICIES = {
    "naming_convention": {"severity": "medium", "description": "Follow naming conventions"},
    "code_review": {"severity": "high", "description": "Require code review before merge"},
    "testing_coverage": {"severity": "high", "description": "Minimum 80% test coverage"},
    "documentation": {"severity": "medium", "description": "API docs required"},
    "security_scan": {"severity": "critical", "description": "Pass security scan"},
    "license_compliance": {"severity": "high", "description": "No banned licenses"},
}


def evaluate_governance(checks: dict[str, bool]) -> dict:
    results = []
    violations = 0
    critical = 0
    for policy_id, info in POLICIES.items():
        passed = checks.get(policy_id, False)
        if not passed:
            violations += 1
            if info["severity"] == "critical":
                critical += 1
        results.append({"policy": policy_id, **info, "passed": passed})
    score = round((len(POLICIES) - violations) / len(POLICIES) * 100)
    return {"results": results, "total": len(POLICIES), "passed": len(POLICIES) - violations,
            "violations": violations, "critical_violations": critical,
            "score": score, "compliant": critical == 0}
