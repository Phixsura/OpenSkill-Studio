"""Fleet AI Sentiment — track sentiment analysis service."""
from __future__ import annotations
def fleet_ai_sentiment(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    analyses_24h = sum(s.get("analyses_24h", 0) for s in services)
    positive_pct = round(sum(s.get("positive_pct", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "analyses_24h": analyses_24h,
            "positive_pct": positive_pct, "all_active": len(active) == len(services)}
