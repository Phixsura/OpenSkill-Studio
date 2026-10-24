"""Fleet Profiler v9 — track application performance profiling sessions."""
from __future__ import annotations
def fleet_profiler_v9(profiles: list[dict]) -> dict:
    completed = [p for p in profiles if p.get("status") == "completed"]
    hotspots = sum(p.get("hotspots", 0) for p in profiles)
    avg_cpu = sum(p.get("cpu_pct", 0) for p in profiles) / len(profiles) if profiles else 0
    return {"total": len(profiles), "completed": len(completed), "hotspots": hotspots,
            "avg_cpu_pct": round(avg_cpu, 1), "healthy": avg_cpu < 80}
