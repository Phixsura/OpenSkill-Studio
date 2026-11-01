"""Fleet AI Model Annotation — track model metadata and tagging."""
from __future__ import annotations
def fleet_ai_model_annotation(annotators: list[dict]) -> dict:
    active = [a for a in annotators if a.get("active", True)]
    models = sum(a.get("models", 0) for a in annotators)
    annotations = sum(a.get("annotations", 0) for a in annotators)
    tags = sum(a.get("tags", 0) for a in annotators)
    return {"annotators": len(annotators), "active": len(active), "models": models,
            "annotations": annotations, "tags": tags, "labeled": annotations > 0}
