"""App review insight — extract actionable insights from user reviews."""

import re
from collections import Counter


SENTIMENT_KEYWORDS = {
    "positive": {"great", "excellent", "amazing", "love", "fantastic", "awesome", "perfect", "best", "easy", "fast"},
    "negative": {"bad", "terrible", "awful", "hate", "slow", "broken", "crash", "bug", "worst", "useless"},
}


def analyze_review_insights(*, reviews: list[dict]) -> dict:
    if not reviews:
        return {"error": "No reviews to analyze"}
    word_freq: Counter = Counter()
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    topics: dict[str, int] = {}
    for review in reviews:
        text = review.get("text", "").lower()
        words = re.findall(r"\b\w{3,}\b", text)
        word_freq.update(words)
        pos_matches = sum(1 for w in words if w in SENTIMENT_KEYWORDS["positive"])
        neg_matches = sum(1 for w in words if w in SENTIMENT_KEYWORDS["negative"])
        if pos_matches > neg_matches:
            sentiment_counts["positive"] += 1
        elif neg_matches > pos_matches:
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1
        for tag in review.get("tags", []):
            topics[tag] = topics.get(tag, 0) + 1
    common_words = [{"word": w, "count": c} for w, c in word_freq.most_common(10)
                     if w not in {"the", "and", "this", "that", "with", "for", "but", "not", "was", "are", "have"}]
    total = len(reviews)
    return {
        "total_reviews": total,
        "sentiment": sentiment_counts,
        "sentiment_score": round((sentiment_counts["positive"] - sentiment_counts["negative"]) / total * 100, 1),
        "common_words": common_words[:8],
        "topics": dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)),
        "avg_rating": round(sum(r.get("rating", 0) for r in reviews) / total, 1),
    }
