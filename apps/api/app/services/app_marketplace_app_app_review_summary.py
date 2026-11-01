"""App review summary — aggregate and summarize app reviews."""


def build_review_summary(*, reviews: list[dict]) -> dict:
    if not reviews:
        return {"total": 0, "avg_rating": 0, "distribution": {}, "sentiment": "neutral"}
    total = len(reviews)
    avg = round(sum(r.get("rating", 0) for r in reviews) / total, 1)
    dist: dict[int, int] = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        rating = r.get("rating", 0)
        if rating in dist:
            dist[rating] += 1
    positive = dist[5] + dist[4]
    negative = dist[1] + dist[2]
    if positive > negative * 2:
        sentiment = "positive"
    elif negative > positive:
        sentiment = "negative"
    else:
        sentiment = "mixed"
    return {
        "total": total,
        "avg_rating": avg,
        "distribution": dist,
        "sentiment": sentiment,
        "positive_pct": round(positive / total * 100, 1),
        "recent": reviews[:3],
    }
