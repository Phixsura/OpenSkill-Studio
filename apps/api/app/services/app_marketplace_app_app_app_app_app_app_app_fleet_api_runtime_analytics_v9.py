"""Fleet API Runtime Analytics v9 — track API runtime behavior analytics."""
from __future__ import annotations
def fleet_api_runtime_analytics_v9(services: list[dict]) -> dict:
    instrumented = [s for s in services if s.get("instrumented")]
    avg_cpu = sum(s.get("cpu_pct", 0) for s in services) / len(services) if services else 0
    avg_mem = sum(s.get("mem_mb", 0) for s in services) / len(services) if services else 0
    return {"services": len(services), "instrumented": len(instrumented),
            "avg_cpu_pct": round(avg_cpu, 1), "avg_mem_mb": round(avg_mem, 1), "healthy": avg_cpu < 80}
