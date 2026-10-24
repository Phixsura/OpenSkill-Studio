"""API endpoint benchmark — benchmark endpoint performance over iterations."""
from __future__ import annotations
import math


def run_benchmark(latencies: list[float], iterations: int) -> dict:
    if not latencies:
        return {"iterations": iterations, "samples": 0}
    s = sorted(latencies)
    n = len(s)
    avg = round(sum(s) / n, 2)
    std = round(math.sqrt(sum((x - avg) ** 2 for x in s) / n), 2)
    return {"iterations": iterations, "samples": n,
            "min_ms": s[0], "max_ms": s[-1], "avg_ms": avg, "std_ms": std,
            "p50_ms": s[n // 2], "p95_ms": s[int(n * 0.95)], "p99_ms": s[int(n * 0.99)],
            "throughput_rps": round(n / max(sum(s) / 1000, 0.001), 1)}


def compare_benchmarks(baseline: dict, current: dict) -> dict:
    if not baseline.get("samples") or not current.get("samples"):
        return {"comparable": False}
    avg_change = round((current["avg_ms"] - baseline["avg_ms"]) / max(baseline["avg_ms"], 0.01) * 100, 1)
    p99_change = round((current["p99_ms"] - baseline["p99_ms"]) / max(baseline["p99_ms"], 0.01) * 100, 1)
    regression = current["p99_ms"] > baseline["p99_ms"] * 1.2
    return {"comparable": True, "avg_change_pct": avg_change, "p99_change_pct": p99_change,
            "regression": regression, "verdict": "regression" if regression else "ok"}
