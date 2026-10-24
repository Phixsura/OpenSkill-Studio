"""Fleet Perf Profile v9 — track continuous profiling results."""
from __future__ import annotations
def fleet_perf_profile_v9(profiles: list[dict]) -> dict:
    cpu_profiles = [p for p in profiles if p.get("type") == "cpu"]
    mem_profiles = [p for p in profiles if p.get("type") == "memory"]
    hotspots = sum(p.get("hotspots_found", 0) for p in profiles)
    return {"total": len(profiles), "cpu": len(cpu_profiles), "memory": len(mem_profiles),
            "hotspots_found": hotspots, "healthy": True}
