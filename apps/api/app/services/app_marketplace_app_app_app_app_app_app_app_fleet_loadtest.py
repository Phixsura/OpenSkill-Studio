"""Fleet load test — track load test results."""
from __future__ import annotations
def fleet_loadtest_results(tests: list[dict]) -> dict:
    passed = [t for t in tests if t.get("passed", False)]
    max_rps = max((t.get("peak_rps", 0) for t in tests), default=0)
    avg_p99 = round(sum(t.get("p99_ms", 0) for t in tests) / max(len(tests), 1), 1)
    return {"total": len(tests), "passed": len(passed), "max_rps": max_rps,
            "avg_p99_ms": avg_p99, "all_passed": len(passed) == len(tests)}
