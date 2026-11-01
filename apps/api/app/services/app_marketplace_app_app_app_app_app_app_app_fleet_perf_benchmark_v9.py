"""Fleet Performance Benchmark v9 — track continuous performance benchmarks."""
from __future__ import annotations
def fleet_perf_benchmark_v9(benchmarks: list[dict]) -> dict:
    passed = [b for b in benchmarks if b.get("passed")]
    regressed = [b for b in benchmarks if b.get("regressed")]
    avg_p99 = sum(b.get("p99_ms", 0) for b in benchmarks) / len(benchmarks) if benchmarks else 0
    return {"total": len(benchmarks), "passed": len(passed), "regressed": len(regressed),
            "avg_p99_ms": round(avg_p99, 1), "healthy": len(regressed) == 0}
