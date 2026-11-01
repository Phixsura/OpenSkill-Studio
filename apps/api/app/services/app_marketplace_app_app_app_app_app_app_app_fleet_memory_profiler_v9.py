"""Fleet Memory Profiler v9 — track application memory usage and leaks."""
from __future__ import annotations
def fleet_memory_profiler_v9(apps: list[dict]) -> dict:
    profiled = [a for a in apps if a.get("profiled")]
    leaks_found = sum(a.get("leaks", 0) for a in apps)
    avg_heap = sum(a.get("heap_mb", 0) for a in apps) / len(apps) if apps else 0
    return {"apps": len(apps), "profiled": len(profiled), "leaks_found": leaks_found,
            "avg_heap_mb": round(avg_heap, 1), "healthy": leaks_found == 0}
