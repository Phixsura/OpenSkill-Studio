"""Performance test runner — execute and report load/perf tests."""
from __future__ import annotations


def run_perf_test(name: str, target_rps: int, duration_sec: int,
                    results: dict) -> dict:
    actual_rps = results.get("actual_rps", 0)
    p99_ms = results.get("p99_ms", 0)
    error_rate = results.get("error_rate_pct", 0)
    achieved_target = actual_rps >= target_rps * 0.95
    latency_ok = p99_ms < results.get("latency_target_ms", 500)
    errors_ok = error_rate < 1
    passed = achieved_target and latency_ok and errors_ok
    return {"test": name, "target_rps": target_rps, "actual_rps": actual_rps,
            "p99_ms": p99_ms, "error_rate": error_rate, "duration_sec": duration_sec,
            "achieved_target": achieved_target, "latency_ok": latency_ok,
            "errors_ok": errors_ok, "passed": passed}


def perf_test_summary(tests: list[dict]) -> dict:
    passed = sum(1 for t in tests if t["passed"])
    return {"total": len(tests), "passed": passed, "failed": len(tests) - passed,
            "pass_rate": round(passed / max(len(tests), 1) * 100)}
