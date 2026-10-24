"""Review analytics — deep analysis of app reviews and ratings."""

from collections import defaultdict


def compute_rating_trends(*, reviews: list[dict]) -> list[dict]:
    by_month: dict[str, list] = defaultdict(list)
    for r in reviews:
        month = r.get("created_at", "")[:7]
        if month:
            by_month[month].append(r.get("rating", 0))
    return [{"month": m, "avg_rating": round(sum(ratings) / len(ratings), 2),
             "review_count": len(ratings)} for m, ratings in sorted(by_month.items())]


def analyze_review_sentiment(*, reviews: list[dict]) -> dict:
    positive = sum(1 for r in reviews if r.get("rating", 0) >= 4)
    negative = sum(1 for r in reviews if r.get("rating", 0) <= 2)
    neutral = len(reviews) - positive - negative
    return {"positive": positive, "neutral": neutral, "negative": negative,
            "positive_pct": round(positive / max(len(reviews), 1) * 100, 1),
            "nps_estimate": round((positive - negative) / max(len(reviews), 1) * 100, 1)}


def find_common_keywords(*, reviews: list[dict], min_count: int = 3) -> list[dict]:
    word_counts: dict[str, int] = defaultdict(int)
    stop_words = {"the", "a", "an", "is", "it", "and", "or", "to", "in", "for", "of", "this", "that", "with"}
    for r in reviews:
        words = set(r.get("text", "").lower().split())
        for w in words - stop_words:
            if len(w) > 3:
                word_counts[w] += 1
    return [{"word": w, "count": c} for w, c in sorted(word_counts.items(), key=lambda x: -x[1]) if c >= min_count][:20]
