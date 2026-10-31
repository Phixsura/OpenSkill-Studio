"""Release candidate evaluator — evaluate if a release candidate is ready."""
from __future__ import annotations


def evaluate_rc(rc: dict) -> dict:
    checks = {
        "tests_passing": rc.get("tests_passing", False),
        "security_scan_clean": rc.get("security_scan_clean", False),
        "performance_acceptable": rc.get("p99_ms", 999) < rc.get("p99_target", 500),
        "error_rate_acceptable": rc.get("error_rate_pct", 100) < rc.get("error_target", 1),
        "code_reviewed": rc.get("code_reviewed", False),
    }
    required_passed = all(v for k, v in checks.items() if k in ("tests_passing", "security_scan_clean", "code_reviewed"))
    all_passed = all(checks.values())
    verdict = "promote" if all_passed else ("hold" if required_passed else "reject")
    return {"verdict": verdict, "checks": checks,
            "passed": sum(1 for v in checks.values() if v),
            "total": len(checks), "version": rc.get("version", "")}
