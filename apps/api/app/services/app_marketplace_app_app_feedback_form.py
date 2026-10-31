"""Feedback form — user feedback collection with sentiment analysis."""

import html
import re

POSITIVE_WORDS = {"great", "love", "amazing", "excellent", "awesome", "perfect", "fast", "easy"}
NEGATIVE_WORDS = {"bad", "terrible", "slow", "broken", "hate", "awful", "crash", "bug"}


def analyze_feedback(*, text: str, rating: int | None = None) -> dict:
    words = set(re.findall(r"\w+", text.lower()))
    pos = words & POSITIVE_WORDS
    neg = words & NEGATIVE_WORDS
    if rating is not None:
        sentiment = "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral"
    elif len(pos) > len(neg):
        sentiment = "positive"
    elif len(neg) > len(pos):
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"text": html.escape(text), "rating": rating, "sentiment": sentiment,
            "positive_signals": list(pos), "negative_signals": list(neg),
            "word_count": len(words)}


def build_feedback_summary(*, feedbacks: list[dict]) -> dict:
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    ratings = [f["rating"] for f in feedbacks if f.get("rating") is not None]
    for f in feedbacks:
        s = analyze_feedback(text=f.get("text", ""), rating=f.get("rating"))
        sentiments[s["sentiment"]] += 1
    avg_rating = round(sum(ratings) / max(len(ratings), 1), 1) if ratings else None
    return {"total": len(feedbacks), "sentiments": sentiments,
            "avg_rating": avg_rating, "rating_count": len(ratings)}
