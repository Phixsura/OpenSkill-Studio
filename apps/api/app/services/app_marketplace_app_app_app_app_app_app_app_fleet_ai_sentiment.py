"""Fleet AI Sentiment Analysis — track opinion and emotion classification."""
from __future__ import annotations
def fleet_ai_sentiment(analyzers: list[dict]) -> dict:
    active = [a for a in analyzers if a.get("active", True)]
    analyzed_24h = sum(a.get("analyzed_24h", 0) for a in analyzers)
    accuracy = round(sum(a.get("accuracy", 0) for a in analyzers) / max(len(analyzers), 1), 1)
    emotions = set()
    for a in analyzers:
        emotions.update(a.get("emotions", []))
    return {"analyzers": len(analyzers), "active": len(active), "analyzed_24h": analyzed_24h,
            "accuracy": accuracy, "emotions": len(emotions), "precise": accuracy > 90}
