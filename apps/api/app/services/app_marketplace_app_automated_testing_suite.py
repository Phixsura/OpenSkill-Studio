"""Automated testing suite — run pre-defined test scenarios against app endpoints."""

from datetime import datetime, timezone


def create_test_suite(*, app_id: str, name: str, test_cases: list[dict]) -> dict:
    if not test_cases:
        return {"error": "At least one test case required"}
    return {"app_id": app_id, "name": name, "test_cases": test_cases,
            "case_count": len(test_cases), "status": "ready", "error": None}


def run_test_case(*, test_case: dict) -> dict:
    expected = test_case.get("expected_status", 200)
    actual = test_case.get("mock_status", 200)
    passed = expected == actual
    body_match = True
    if test_case.get("expected_body_contains"):
        body_match = test_case["expected_body_contains"] in test_case.get("mock_body", "")
    return {"name": test_case.get("name", "unnamed"), "passed": passed and body_match,
            "expected_status": expected, "actual_status": actual,
            "body_match": body_match, "duration_ms": test_case.get("mock_duration", 10)}


def run_full_suite(*, test_cases: list[dict]) -> dict:
    results = [run_test_case(test_case=tc) for tc in test_cases]
    passed = sum(1 for r in results if r["passed"])
    total_ms = sum(r["duration_ms"] for r in results)
    return {"results": results, "passed": passed, "failed": len(results) - passed,
            "total": len(results), "pass_rate": round(passed / max(len(results), 1) * 100, 1),
            "total_duration_ms": total_ms, "run_at": datetime.now(timezone.utc).isoformat()}
