"""API change impact scorer — score the impact of API changes."""
from __future__ import annotations


def score_change(change: dict) -> dict:
    score = 0
    factors = []
    if change.get("breaking"):
        score += 40
        factors.append("breaking_change")
    if change.get("affects_auth"):
        score += 20
        factors.append("auth_change")
    consumers = change.get("consumer_count", 0)
    if consumers > 100:
        score += 30
        factors.append("many_consumers")
    elif consumers > 10:
        score += 15
        factors.append("some_consumers")
    if change.get("data_model_change"):
        score += 25
        factors.append("data_model")
    if change.get("env") == "production":
        score += 10
        factors.append("production")
    risk = "critical" if score >= 70 else ("high" if score >= 40 else ("medium" if score >= 20 else "low"))
    return {"score": min(score, 100), "risk": risk, "factors": factors}


def batch_score(changes: list[dict]) -> dict:
    results = [score_change(c) for c in changes]
    critical = sum(1 for r in results if r["risk"] == "critical")
    high = sum(1 for r in results if r["risk"] == "high")
    return {"total": len(results), "critical": critical, "high": high,
            "max_score": max(r["score"] for r in results) if results else 0}
