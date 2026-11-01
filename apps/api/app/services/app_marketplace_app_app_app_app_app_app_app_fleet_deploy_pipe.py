"""Fleet deployment pipeline — track CI/CD pipeline health."""
from __future__ import annotations
def fleet_deploy_pipeline(pipelines: list[dict]) -> dict:
    passing = [p for p in pipelines if p.get("status") == "passing"]
    failing = [p for p in pipelines if p.get("status") == "failing"]
    avg_duration = round(sum(p.get("duration_min", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    return {"total": len(pipelines), "passing": len(passing), "failing": len(failing),
            "avg_duration_min": avg_duration, "healthy": len(failing) == 0}
