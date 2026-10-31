"""User feedback — in-app feedback collection and sentiment analysis."""

import re


def create_feedback(*, app_id: str, user_id: str, type: str, message: str,
                      page: str | None = None) -> dict:
    valid_types = {"bug", "feature", "improvement", "praise", "other"}
    if type not in valid_types:
        return {"error": f"Invalid type. Use: {', '.join(sorted(valid_types))}"}
    if len(message) < 5:
        return {"error": "Message too short"}
    return {"app_id": app_id, "user_id": user_id, "type": type, "message": message,
            "page": page, "status": "new", "error": None}


def analyze_sentiment(*, message: str) -> dict:
    positive = {"great", "love", "excellent", "awesome", "fantastic", "perfect", "amazing"}
    negative = {"bad", "terrible", "awful", "broken", "hate", "worst", "crash"}
    words = set(re.findall(r'\w+', message.lower()))
    pos = len(words & positive)
    neg = len(words & negative)
    if pos > neg:
        return {"sentiment": "positive", "score": min(1.0, pos * 0.3)}
    elif neg > pos:
        return {"sentiment": "negative", "score": min(1.0, neg * 0.3)}
    return {"sentiment": "neutral", "score": 0}


def categorize_feedback(*, feedbacks: list[dict]) -> dict:
    by_type: dict[str, int] = {}
    by_sentiment: dict[str, int] = {}
    for f in feedbacks:
        t = f.get("type", "other")
        by_type[t] = by_type.get(t, 0) + 1
        s = f.get("sentiment", "neutral")
        by_sentiment[s] = by_sentiment.get(s, 0) + 1
    return {"by_type": by_type, "by_sentiment": by_sentiment, "total": len(feedbacks)}
