"""Fleet CPU Profiler v9 — track CPU usage hotspots and flame graphs."""
from __future__ import annotations
def fleet_cpu_profiler_v9(profiles: list[dict]) -> dict:
    collected = [p for p in profiles if p.get("collected")]
    hotspots = sum(p.get("hotspots", 0) for p in profiles)
    avg_cpu = sum(p.get("cpu_pct", 0) for p in profiles) / len(profiles) if profiles else 0
    return {"profiles": len(profiles), "collected": len(collected), "hotspots": hotspots,
            "avg_cpu_pct": round(avg_cpu, 1), "healthy": avg_cpu < 80}
