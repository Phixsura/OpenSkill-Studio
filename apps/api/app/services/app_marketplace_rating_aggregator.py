"""Rating aggregator — weighted average, distribution histogram, helpful votes."""

import math


def compute_weighted_rating(*, ratings: list[dict], min_votes: int = 5) -> dict:
    if not ratings:
        return {"average": 0, "count": 0, "weighted_score": 0, "confidence": "low"}
    total = sum(r["score"] for r in ratings)
    count = len(ratings)
    average = total / count
    # Bayesian average with global mean of 3.0
    global_mean = 3.0
    weighted = (count * average + min_votes * global_mean) / (count + min_votes)
    confidence = "high" if count >= 50 else "medium" if count >= 10 else "low"
    return {"average": round(average, 2), "count": count, "weighted_score": round(weighted, 2), "confidence": confidence}


def build_distribution(*, ratings: list[dict]) -> dict:
    dist = {str(i): 0 for i in range(1, 6)}
    for r in ratings:
        key = str(min(5, max(1, r["score"])))
        dist[key] += 1
    total = len(ratings) or 1
    percentages = {k: round(v / total * 100, 1) for k, v in dist.items()}
    return {"counts": dist, "percentages": percentages}


def sort_reviews_by_helpfulness(*, reviews: list[dict]) -> list[dict]:
    def wilson_score(r: dict) -> float:
        up = r.get("helpful_yes", 0)
        total = up + r.get("helpful_no", 0)
        if total == 0:
            return 0
        p = up / total
        z = 1.96
        denom = 1 + z * z / total
        center = p + z * z / (2 * total)
        spread = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
        return (center - spread) / denom
    return sorted(reviews, key=wilson_score, reverse=True)
