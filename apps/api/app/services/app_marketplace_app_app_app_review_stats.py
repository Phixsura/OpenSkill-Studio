"""App review stats — review statistics with sentiment breakdown."""

import html
from collections import Counter


def build_review_stats(*, reviews: list[dict]) -> dict:
    if not reviews:
        return {"total": 0, "avg_rating": 0, "distribution": {i: 0 for i in range(1, 6)},
                "sentiment": {"positive": 0, "neutral": 0, "negative": 0},
                "nps": 0, "stars": "☆☆☆☆☆"}
    ratings = [r.get("rating", 0) for r in reviews]
    avg = round(sum(ratings) / len(ratings), 1)
    dist = Counter(ratings)
    distribution = {i: dist.get(i, 0) for i in range(1, 6)}
    positive = sum(1 for r in ratings if r >= 4)
    neutral = sum(1 for r in ratings if r == 3)
    negative = sum(1 for r in ratings if r <= 2)
    promoters = sum(1 for r in ratings if r >= 5)
    detractors = sum(1 for r in ratings if r <= 2)
    nps = round((promoters - detractors) / len(ratings) * 100)
    stars = "★" * round(avg) + "☆" * (5 - round(avg))
    return {"total": len(reviews), "avg_rating": avg, "distribution": distribution,
            "sentiment": {"positive": positive, "neutral": neutral, "negative": negative},
            "nps": nps, "stars": stars,
            "recommendation_pct": round(positive / len(reviews) * 100)}
