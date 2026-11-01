"""Fleet AI Platform CD v2 — track continuous delivery for AI platform."""
from __future__ import annotations
def fleet_ai_platform_cd_v2(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    deploys_24h = sum(p.get("deploys_24h", 0) for p in pipelines)
    rollbacks = sum(p.get("rollbacks", 0) for p in pipelines)
    lead_time_min = round(sum(p.get("lead_time_min", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    return {"pipelines": len(pipelines), "active": len(active), "deploys_24h": deploys_24h,
            "rollbacks": rollbacks, "lead_time_min": lead_time_min, "elite": lead_time_min < 15}
