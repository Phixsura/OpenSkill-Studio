"""Compliance checker — verify apps meet marketplace security and privacy standards."""

REQUIRED_CHECKS = [
    {"id": "manifest_valid", "label": "Valid manifest", "category": "structure"},
    {"id": "no_secrets_in_code", "label": "No hardcoded secrets", "category": "security"},
    {"id": "https_only", "label": "HTTPS-only endpoints", "category": "security"},
    {"id": "privacy_policy", "label": "Privacy policy provided", "category": "privacy"},
    {"id": "data_handling", "label": "Data handling declaration", "category": "privacy"},
    {"id": "error_handling", "label": "Proper error handling", "category": "quality"},
    {"id": "rate_limiting", "label": "Rate limiting implemented", "category": "quality"},
    {"id": "documentation", "label": "Documentation provided", "category": "quality"},
]


def run_compliance_check(*, app: dict, completed_checks: list[str]) -> dict:
    results = []
    for check in REQUIRED_CHECKS:
        passed = check["id"] in completed_checks
        results.append({**check, "passed": passed})
    passed_count = sum(1 for r in results if r["passed"])
    score = round(passed_count / len(REQUIRED_CHECKS) * 100)
    return {
        "results": results, "score": score,
        "passed": passed_count, "total": len(REQUIRED_CHECKS),
        "compliant": score >= 80,
        "blocking_issues": [r for r in results if not r["passed"] and r["category"] == "security"],
    }


def get_compliance_recommendations(*, results: list[dict]) -> list[str]:
    recs = []
    for r in results:
        if not r["passed"]:
            recs.append(f"Fix: {r['label']} ({r['category']})")
    return recs
