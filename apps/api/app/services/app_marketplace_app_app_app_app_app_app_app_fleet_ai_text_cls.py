"""Fleet AI Text Classifier v2 — track zero-shot and few-shot text classification."""
from __future__ import annotations
def fleet_ai_text_classifier(classifiers: list[dict]) -> dict:
    active = [c for c in classifiers if c.get("active", True)]
    classified_24h = sum(c.get("classified_24h", 0) for c in classifiers)
    labels = sum(c.get("labels", 0) for c in classifiers)
    zero_shot_pct = round(sum(c.get("zero_shot_pct", 0) for c in classifiers) / max(len(classifiers), 1), 1)
    f1 = round(sum(c.get("f1", 0) for c in classifiers) / max(len(classifiers), 1), 2)
    return {"classifiers": len(classifiers), "active": len(active), "classified_24h": classified_24h,
            "labels": labels, "zero_shot_pct": zero_shot_pct, "f1": f1, "accurate": f1 > 0.85}
