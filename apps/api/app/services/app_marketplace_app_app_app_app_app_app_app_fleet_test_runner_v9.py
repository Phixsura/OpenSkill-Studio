"""Fleet Test Runner v9 — track CI test suite execution and flakiness."""
from __future__ import annotations
def fleet_test_runner_v9(suites: list[dict]) -> dict:
    passed = sum(s.get("passed", 0) for s in suites)
    failed = sum(s.get("failed", 0) for s in suites)
    flaky = sum(s.get("flaky", 0) for s in suites)
    duration = sum(s.get("duration_sec", 0) for s in suites)
    return {"suites": len(suites), "passed": passed, "failed": failed,
            "flaky": flaky, "total_duration_sec": duration, "healthy": failed == 0}
