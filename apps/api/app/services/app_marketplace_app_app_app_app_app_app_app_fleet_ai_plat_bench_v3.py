"""Fleet AI Platform Benchmark v3 — track platform-wide performance benchmarks."""
from __future__ import annotations
def fleet_ai_platform_benchmark_v3(benches: list[dict]) -> dict:
    active = [b for b in benches if b.get("active", True)]
    tests = sum(b.get("tests", 0) for b in benches)
    p99_ms = round(sum(b.get("p99_ms", 0) for b in benches) / max(len(benches), 1), 1)
    throughput = sum(b.get("throughput_rps", 0) for b in benches)
    return {"benches": len(benches), "active": len(active), "tests": tests,
            "p99_ms": p99_ms, "throughput": throughput, "performant": p99_ms < 100}
