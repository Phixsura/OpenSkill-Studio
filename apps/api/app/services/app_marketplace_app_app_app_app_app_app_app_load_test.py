"""API load test runner — simulate and report load test results."""
from __future__ import annotations


def run_load_test(endpoint: str, rps: int, duration_sec: int,
                   avg_latency_ms: float, error_rate_pct: float) -> dict:
    total_requests = rps * duration_sec
    successful = int(total_requests * (1 - error_rate_pct / 100))
    failed = total_requests - successful
    throughput = round(successful / duration_sec, 1)
    return {"endpoint": endpoint, "rps": rps, "duration_sec": duration_sec,
            "total_requests": total_requests, "successful": successful, "failed": failed,
            "avg_latency_ms": avg_latency_ms, "error_rate_pct": error_rate_pct,
            "throughput_rps": throughput,
            "passed": error_rate_pct < 1 and avg_latency_ms < 500}


def compare_runs(current: dict, baseline: dict) -> dict:
    latency_delta = round(current["avg_latency_ms"] - baseline["avg_latency_ms"], 1)
    error_delta = round(current["error_rate_pct"] - baseline["error_rate_pct"], 2)
    return {"latency_change_ms": latency_delta, "error_change_pct": error_delta,
            "regression": latency_delta > 50 or error_delta > 0.5,
            "improved": latency_delta < -20 and error_delta <= 0}
