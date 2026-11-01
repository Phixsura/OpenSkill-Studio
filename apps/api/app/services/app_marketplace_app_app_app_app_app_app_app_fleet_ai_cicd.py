"""Fleet AI CI/CD — track AI model continuous integration and delivery."""
from __future__ import annotations
def fleet_ai_cicd(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    builds_24h = sum(p.get("builds_24h", 0) for p in pipelines)
    deploys_24h = sum(p.get("deploys_24h", 0) for p in pipelines)
    success_rate = round(sum(p.get("success_pct", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    return {"pipelines": len(pipelines), "active": len(active), "builds_24h": builds_24h,
            "deploys_24h": deploys_24h, "success_rate": success_rate, "reliable": success_rate > 95}
