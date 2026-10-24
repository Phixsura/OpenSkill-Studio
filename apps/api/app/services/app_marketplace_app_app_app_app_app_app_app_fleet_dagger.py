"""Fleet Dagger — track programmable CI/CD engine metrics."""
from __future__ import annotations
def fleet_dagger_status(pipelines: list[dict]) -> dict:
    cached = sum(p.get("cache_hits", 0) for p in pipelines)
    total_ops = sum(p.get("operations", 0) for p in pipelines)
    avg_dur = round(sum(p.get("duration_sec", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    return {"pipelines": len(pipelines), "cache_hits": cached, "operations": total_ops,
            "avg_duration_sec": avg_dur, "fast": avg_dur < 300}
