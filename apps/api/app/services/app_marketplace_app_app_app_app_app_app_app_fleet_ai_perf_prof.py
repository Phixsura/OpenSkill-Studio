"""Fleet AI Performance Profiler — track AI system performance bottlenecks."""
from __future__ import annotations
def fleet_ai_perf_profiler(profilers: list[dict]) -> dict:
    active = [p for p in profilers if p.get("active", True)]
    profiles_24h = sum(p.get("profiles_24h", 0) for p in profilers)
    bottlenecks_found = sum(p.get("bottlenecks", 0) for p in profilers)
    optimizations = sum(p.get("optimizations", 0) for p in profilers)
    return {"profilers": len(profilers), "active": len(active), "profiles_24h": profiles_24h,
            "bottlenecks": bottlenecks_found, "optimizations": optimizations, "improving": optimizations > 0}
