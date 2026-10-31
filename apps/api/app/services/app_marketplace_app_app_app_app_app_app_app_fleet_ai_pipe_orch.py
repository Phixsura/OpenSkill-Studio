"""Fleet AI Pipeline Orchestrator — track end-to-end ML pipeline execution."""
from __future__ import annotations
def fleet_ai_pipeline_orchestrator(orchestrators: list[dict]) -> dict:
    active = [o for o in orchestrators if o.get("active", True)]
    pipelines_24h = sum(o.get("pipelines_24h", 0) for o in orchestrators)
    stages = sum(o.get("stages", 0) for o in orchestrators)
    success_rate = round(sum(o.get("success_pct", 0) for o in orchestrators) / max(len(orchestrators), 1), 1)
    return {"orchestrators": len(orchestrators), "active": len(active), "pipelines_24h": pipelines_24h,
            "stages": stages, "success_rate": success_rate, "reliable": success_rate > 95}
