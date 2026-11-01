"""Fleet Bazel — track build system performance."""
from __future__ import annotations
def fleet_bazel_status(builds: list[dict]) -> dict:
    cached = sum(b.get("cache_hit_pct", 0) for b in builds) / max(len(builds), 1)
    avg_time = round(sum(b.get("build_sec", 0) for b in builds) / max(len(builds), 1), 1)
    remote_exec = [b for b in builds if b.get("remote_execution", False)]
    return {"total_builds": len(builds), "avg_cache_hit_pct": round(cached, 1),
            "avg_build_sec": avg_time, "remote_execution": len(remote_exec), "fast": avg_time < 120}
