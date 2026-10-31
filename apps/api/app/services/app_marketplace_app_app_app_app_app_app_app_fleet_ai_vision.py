"""Fleet AI Vision — track computer vision and image understanding."""
from __future__ import annotations
def fleet_ai_vision(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    images_24h = sum(p.get("images_24h", 0) for p in pipelines)
    accuracy = round(sum(p.get("accuracy", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    models = len(set(p.get("model", "") for p in pipelines))
    return {"pipelines": len(pipelines), "active": len(active), "images_24h": images_24h,
            "accuracy": accuracy, "models": models, "precise": accuracy > 95}
