"""Fleet Turborepo — track monorepo build cache."""
from __future__ import annotations
def fleet_turborepo_status(tasks: list[dict]) -> dict:
    cached = [t for t in tasks if t.get("cache_status") == "HIT"]
    miss = [t for t in tasks if t.get("cache_status") == "MISS"]
    time_saved = sum(t.get("time_saved_sec", 0) for t in cached)
    return {"total_tasks": len(tasks), "cache_hits": len(cached), "cache_misses": len(miss),
            "time_saved_sec": time_saved, "hit_rate": round(len(cached) / max(len(tasks), 1) * 100, 1)}
