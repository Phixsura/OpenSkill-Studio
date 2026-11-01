"""Fleet GC pressure — track garbage collection across JVM/runtime services."""
from __future__ import annotations
def fleet_gc_pressure(services: list[dict]) -> dict:
    total_pause = sum(s.get("gc_pause_ms", 0) for s in services)
    avg_pause = round(total_pause / max(len(services), 1), 1)
    return {"avg_gc_pause_ms": avg_pause, "total_pause_ms": total_pause,
            "high_pressure": avg_pause > 200, "services": len(services)}
