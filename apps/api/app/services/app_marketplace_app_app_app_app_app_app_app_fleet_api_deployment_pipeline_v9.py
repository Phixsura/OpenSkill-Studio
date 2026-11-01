"""Fleet API Deployment Pipeline v9 — track API deployment CI/CD pipeline."""
from __future__ import annotations
def fleet_api_deployment_pipeline_v9(pipelines: list[dict]) -> dict:
    success = [p for p in pipelines if p.get("status") == "success"]
    failed = [p for p in pipelines if p.get("status") == "failed"]
    avg_duration = sum(p.get("duration_sec", 0) for p in pipelines) / len(pipelines) if pipelines else 0
    return {"pipelines": len(pipelines), "success": len(success), "failed": len(failed),
            "avg_duration_sec": round(avg_duration, 1), "healthy": len(failed) == 0}
