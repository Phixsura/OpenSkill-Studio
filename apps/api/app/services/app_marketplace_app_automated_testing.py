"""Automated testing — run CI test suites for apps before publish."""

import secrets
from datetime import datetime


def run_test_pipeline(*, app_id: str, test_suites: list[dict]) -> dict:
    results = []
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    for suite in test_suites:
        passed = suite.get("passed", 0)
        failed = suite.get("failed", 0)
        skipped = suite.get("skipped", 0)
        total_passed += passed
        total_failed += failed
        total_skipped += skipped
        duration = suite.get("duration_ms", 0)
        results.append({
            "name": suite["name"],
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": passed + failed + skipped,
            "duration_ms": duration,
            "status": "passed" if failed == 0 else "failed",
        })
    all_passed = total_failed == 0
    return {
        "run_id": f"run_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "suites": results,
        "summary": {"passed": total_passed, "failed": total_failed, "skipped": total_skipped,
                     "total": total_passed + total_failed + total_skipped},
        "all_passed": all_passed,
        "publishable": all_passed,
        "completed_at": datetime.utcnow().isoformat(),
    }
