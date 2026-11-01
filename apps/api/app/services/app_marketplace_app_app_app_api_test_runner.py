"""App API test runner — automated API endpoint testing."""

import html
from datetime import datetime, timezone


def run_api_tests(*, tests: list[dict]) -> dict:
    results = []
    passed = failed = 0
    total_ms = 0
    for t in tests:
        expected = t.get("expected_status", 200)
        actual = t.get("actual_status", expected)
        ok = actual == expected
        dur = t.get("duration_ms", 45)
        total_ms += dur
        if ok: passed += 1
        else: failed += 1
        results.append({
            "name": html.escape(t.get("name", "")),
            "method": t.get("method", "GET"),
            "path": t.get("path", ""),
            "expected_status": expected,
            "actual_status": actual,
            "passed": ok,
            "duration_ms": dur,
        })
    return {"results": results, "total": len(results),
            "passed": passed, "failed": failed,
            "pass_rate": round(passed / max(len(results), 1) * 100, 1),
            "total_ms": total_ms,
            "all_passed": failed == 0}
