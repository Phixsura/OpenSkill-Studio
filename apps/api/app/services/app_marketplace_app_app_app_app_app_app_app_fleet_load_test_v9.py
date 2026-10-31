"""Fleet Load Test v9 — track load testing results and capacity limits."""
from __future__ import annotations
def fleet_load_test_v9(tests: list[dict]) -> dict:
    passed = [t for t in tests if t.get("passed")]
    max_rps = max((t.get("peak_rps", 0) for t in tests), default=0)
    avg_p99 = sum(t.get("p99_ms", 0) for t in tests) / len(tests) if tests else 0
    return {"tests": len(tests), "passed": len(passed), "max_rps": max_rps,
            "avg_p99_ms": round(avg_p99, 1), "healthy": len(passed) == len(tests)}
