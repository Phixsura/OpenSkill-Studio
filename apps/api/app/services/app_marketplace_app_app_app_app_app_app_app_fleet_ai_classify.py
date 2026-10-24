"""Fleet AI Classification — track text and image classification."""
from __future__ import annotations
def fleet_ai_classification(classifiers: list[dict]) -> dict:
    active = [c for c in classifiers if c.get("active", True)]
    predictions_24h = sum(c.get("predictions_24h", 0) for c in classifiers)
    classes = sum(c.get("classes", 0) for c in classifiers)
    accuracy = round(sum(c.get("accuracy", 0) for c in classifiers) / max(len(classifiers), 1), 1)
    return {"classifiers": len(classifiers), "active": len(active), "predictions_24h": predictions_24h,
            "classes": classes, "accuracy": accuracy, "precise": accuracy > 95}
