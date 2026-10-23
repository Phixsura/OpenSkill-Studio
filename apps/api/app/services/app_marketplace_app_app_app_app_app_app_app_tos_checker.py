"""Terms of service checker — validate app compliance with platform TOS."""
from __future__ import annotations

TOS_RULES = [
    {"id": "data_privacy", "title": "Data Privacy", "description": "Must have privacy policy", "required": True},
    {"id": "no_malware", "title": "No Malware", "description": "No malicious code or behavior", "required": True},
    {"id": "rate_limits", "title": "Rate Limits", "description": "Must respect API rate limits", "required": True},
    {"id": "branding", "title": "Branding Guidelines", "description": "Follow OpenSkill branding rules", "required": False},
    {"id": "support", "title": "User Support", "description": "Provide support channel", "required": False},
]


def check_compliance(app_checks: dict[str, bool]) -> dict:
    results = []
    for rule in TOS_RULES:
        passed = app_checks.get(rule["id"], False)
        results.append({**rule, "passed": passed,
                         "critical": rule["required"] and not passed})
    required_passed = all(r["passed"] for r in results if r["required"])
    total_passed = sum(1 for r in results if r["passed"])
    return {"results": results, "compliant": required_passed,
            "passed": total_passed, "total": len(results),
            "score": round(total_passed / len(results) * 100)}
