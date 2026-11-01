"""Fleet AI Platform CI v2 — track continuous integration for AI platform."""
from __future__ import annotations
def fleet_ai_platform_ci_v2(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    builds_24h = sum(p.get("builds_24h", 0) for p in pipelines)
    pass_rate = round(sum(p.get("pass_rate", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    avg_duration_min = round(sum(p.get("duration_min", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    return {"pipelines": len(pipelines), "active": len(active), "builds_24h": builds_24h,
            "pass_rate": pass_rate, "duration_min": avg_duration_min, "green": pass_rate > 95}
