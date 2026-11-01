"""Fleet ML Pipeline v9 — track ML training and inference pipelines."""
from __future__ import annotations
def fleet_ml_pipeline_v9(pipelines: list[dict]) -> dict:
    training = [p for p in pipelines if p.get("phase") == "training"]
    inference = [p for p in pipelines if p.get("phase") == "inference"]
    gpu_hours = sum(p.get("gpu_hours", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "training": len(training), "inference": len(inference),
            "gpu_hours": round(gpu_hours, 1), "healthy": True}
