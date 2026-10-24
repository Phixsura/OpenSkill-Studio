"""App rating aggregator — Wilson score and distribution analysis."""
from __future__ import annotations
import math


def wilson_score(positive: int, total: int, *, confidence: float = 0.95) -> float:
    if total == 0:
        return 0.0
    z = 1.96 if confidence == 0.95 else 2.576
    p = positive / total
    score = (p + z * z / (2 * total) - z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)) / (1 + z * z / total)
    return round(max(0, score), 4)


def aggregate_ratings(reviews: list[dict]) -> dict:
    if not reviews:
        return {"count": 0, "average": 0, "distribution": {}, "wilson": 0}
    ratings = [r.get("rating", 0) for r in reviews]
    avg = round(sum(ratings) / len(ratings), 1)
    dist = {i: ratings.count(i) for i in range(1, 6)}
    positive = sum(1 for r in ratings if r >= 4)
    ws = wilson_score(positive, len(ratings))
    return {"count": len(ratings), "average": avg,
            "average_display": f"{avg} ⭐",
            "distribution": dist, "wilson_score": ws,
            "sentiment": "positive" if avg >= 4 else "mixed" if avg >= 3 else "negative"}
