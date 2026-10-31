"""Fleet AI Model Compression — track quantization and pruning pipelines."""
from __future__ import annotations
def fleet_ai_model_compression(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    models_compressed = sum(p.get("models_compressed", 0) for p in pipelines)
    avg_reduction = round(sum(p.get("size_reduction_pct", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    quality_loss = round(sum(p.get("quality_loss_pct", 0) for p in pipelines) / max(len(pipelines), 1), 2)
    return {"pipelines": len(pipelines), "active": len(active), "models_compressed": models_compressed,
            "avg_reduction": avg_reduction, "quality_loss": quality_loss, "efficient": avg_reduction > 50 and quality_loss < 2}
