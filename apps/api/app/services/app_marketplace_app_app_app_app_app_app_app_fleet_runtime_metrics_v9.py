"""Fleet Runtime Metrics v9 — track application runtime memory and CPU."""
from __future__ import annotations
def fleet_runtime_metrics_v9(apps: list[dict]) -> dict:
    total_memory_gb = sum(a.get("memory_gb", 0) for a in apps)
    total_cpu = sum(a.get("cpu_cores", 0) for a in apps)
    gc_pauses = sum(a.get("gc_pause_ms", 0) for a in apps)
    return {"apps": len(apps), "total_memory_gb": round(total_memory_gb, 1),
            "total_cpu_cores": total_cpu, "gc_pause_ms": gc_pauses, "healthy": gc_pauses < 100}
