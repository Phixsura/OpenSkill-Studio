"""Review analytics v2 — deep review analysis with sentiment, keywords, and trends."""

from collections import defaultdict


def analyze_reviews_v2(*, reviews: list[dict]) -> dict:
    if not reviews:
        return {"total": 0, "avg_rating": 0, "sentiment": {}, "trends": [], "keywords": []}
    total = len(reviews)
    avg = round(sum(r.get("rating", 0) for r in reviews) / total, 2)
    positive = sum(1 for r in reviews if r.get("rating", 0) >= 4)
    negative = sum(1 for r in reviews if r.get("rating", 0) <= 2)
    neutral = total - positive - negative
    # Monthly trends
    by_month = defaultdict(lambda: {"count": 0, "total_rating": 0})
    for r in reviews:
        month = r.get("created_at", "")[:7]
        if month:
            by_month[month]["count"] += 1
            by_month[month]["total_rating"] += r.get("rating", 0)
    trends = [{"month": m, "count": d["count"],
                "avg_rating": round(d["total_rating"] / d["count"], 2)}
              for m, d in sorted(by_month.items())]
    # Keyword extraction
    word_counts = defaultdict(int)
    stop_words = {"the", "a", "an", "is", "it", "and", "or", "to", "in", "for", "of", "this", "that", "with", "very", "app"}
    for r in reviews:
        words = set(r.get("body", "").lower().split())
        for w in words - stop_words:
            if len(w) > 3:
                word_counts[w] += 1
    keywords = [{"word": w, "count": c} for w, c in sorted(word_counts.items(), key=lambda x: -x[1])[:15]]
    return {
        "total": total, "avg_rating": avg,
        "sentiment": {"positive": positive, "neutral": neutral, "negative": negative,
                        "nps": round((positive - negative) / total * 100, 1)},
        "trends": trends, "keywords": keywords,
        "reply_rate": round(sum(1 for r in reviews if r.get("has_reply")) / total * 100, 1),
    }
