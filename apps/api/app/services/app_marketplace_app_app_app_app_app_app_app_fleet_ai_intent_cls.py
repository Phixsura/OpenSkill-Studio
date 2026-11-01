"""Fleet AI Intent Classifier — track user intent classification."""
from __future__ import annotations
def fleet_ai_intent_classifier(classifiers: list[dict]) -> dict:
    active = [c for c in classifiers if c.get("active", True)]
    classified_24h = sum(c.get("classified_24h", 0) for c in classifiers)
    intents = sum(c.get("intents", 0) for c in classifiers)
    accuracy = round(sum(c.get("accuracy", 0) for c in classifiers) / max(len(classifiers), 1), 1)
    return {"classifiers": len(classifiers), "active": len(active), "classified_24h": classified_24h,
            "intents": intents, "accuracy": accuracy, "precise": accuracy > 90}
