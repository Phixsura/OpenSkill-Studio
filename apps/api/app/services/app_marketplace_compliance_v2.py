"""Compliance v2 — automated compliance checks with remediation guidance."""

COMPLIANCE_RULES = {
    "data_encryption": {"label": "Data encrypted at rest", "category": "security", "severity": "critical"},
    "access_logging": {"label": "Access logging enabled", "category": "audit", "severity": "high"},
    "input_validation": {"label": "Input validation on all endpoints", "category": "security", "severity": "critical"},
    "rate_limiting": {"label": "Rate limiting configured", "category": "availability", "severity": "medium"},
    "error_handling": {"label": "Proper error handling (no stack traces)", "category": "security", "severity": "high"},
    "privacy_policy": {"label": "Privacy policy published", "category": "legal", "severity": "high"},
    "data_retention": {"label": "Data retention policy defined", "category": "legal", "severity": "medium"},
    "backup_strategy": {"label": "Backup strategy documented", "category": "availability", "severity": "medium"},
}


def run_compliance_audit(*, completed_rules: list[str]) -> dict:
    results = []
    for rule_id, rule in COMPLIANCE_RULES.items():
        passed = rule_id in completed_rules
        results.append({"id": rule_id, **rule, "passed": passed})
    passed_count = sum(1 for r in results if r["passed"])
    critical_failures = [r for r in results if not r["passed"] and r["severity"] == "critical"]
    return {"results": results, "passed": passed_count, "total": len(results),
            "score": round(passed_count / len(results) * 100),
            "critical_failures": len(critical_failures), "compliant": len(critical_failures) == 0}


def get_remediation_steps(*, failed_rules: list[str]) -> list[dict]:
    remediation = {
        "data_encryption": "Enable encryption using the platform's built-in encryption service",
        "access_logging": "Enable access logging in Settings > Security > Audit Log",
        "input_validation": "Add request validation middleware to all API endpoints",
        "rate_limiting": "Configure rate limits in Settings > API > Rate Limits",
        "error_handling": "Ensure all error responses use structured error format without stack traces",
        "privacy_policy": "Add privacy policy URL in Settings > Legal",
        "data_retention": "Define data retention policy in Settings > Data Management",
        "backup_strategy": "Document backup procedures in your app's documentation",
    }
    return [{"rule": r, "steps": remediation.get(r, "Contact support")} for r in failed_rules if r in remediation]
