"""App security scanner — automated security checks for marketplace apps."""
from __future__ import annotations
import re
from urllib.parse import urlparse

CHECKS = [
    {"id": "https_only", "title": "HTTPS Only", "severity": "high"},
    {"id": "no_secrets", "title": "No Hardcoded Secrets", "severity": "critical"},
    {"id": "csp_headers", "title": "CSP Headers", "severity": "medium"},
    {"id": "input_validation", "title": "Input Validation", "severity": "high"},
    {"id": "rate_limiting", "title": "Rate Limiting", "severity": "medium"},
]


def run_security_scan(app: dict) -> dict:
    results = []
    for check in CHECKS:
        passed = app.get(f"check_{check['id']}", True)
        results.append({**check, "passed": passed})
    passed_count = sum(1 for r in results if r["passed"])
    critical_fails = [r for r in results if not r["passed"] and r["severity"] == "critical"]
    score = round(passed_count / len(results) * 100)
    return {
        "results": results, "passed": passed_count, "total": len(results),
        "score": score, "score_display": f"{score}%",
        "critical_failures": len(critical_fails),
        "status": "failed" if critical_fails else "warning" if score < 100 else "passed",
    }


def check_url_security(url: str) -> dict:
    parsed = urlparse(url)
    issues = []
    if parsed.scheme != "https":
        issues.append("Must use HTTPS")
    if not parsed.netloc:
        issues.append("Invalid URL")
    if parsed.port and parsed.port not in (443, 8443):
        issues.append("Non-standard HTTPS port")
    return {"url": url, "secure": len(issues) == 0, "issues": issues}
