"""Load test runner — define and analyze load test results."""
from __future__ import annotations


def analyze_load_test(results: dict) -> dict:
    total_reqs = results.get("total_requests", 0)
    failed = results.get("failed_requests", 0)
    duration_s = results.get("duration_seconds", 1)
    rps = round(total_reqs / max(duration_s, 0.01), 1)
    error_rate = round(failed / max(total_reqs, 1) * 100, 2)
    p50 = results.get("p50_ms", 0)
    p95 = results.get("p95_ms", 0)
    p99 = results.get("p99_ms", 0)
    passed = error_rate < 1 and p99 < results.get("max_p99_ms", 1000)
    return {"rps": rps, "total_requests": total_reqs, "error_rate_pct": error_rate,
            "p50_ms": p50, "p95_ms": p95, "p99_ms": p99,
            "duration_seconds": duration_s, "passed": passed}


def compare_runs(baseline: dict, current: dict) -> dict:
    rps_change = round((current["rps"] - baseline["rps"]) / max(baseline["rps"], 0.01) * 100, 1)
    p99_change = round((current["p99_ms"] - baseline["p99_ms"]) / max(baseline["p99_ms"], 0.01) * 100, 1)
    regression = current["p99_ms"] > baseline["p99_ms"] * 1.2 or current["error_rate_pct"] > baseline["error_rate_pct"] * 2
    return {"rps_change_pct": rps_change, "p99_change_pct": p99_change,
            "regression": regression}
