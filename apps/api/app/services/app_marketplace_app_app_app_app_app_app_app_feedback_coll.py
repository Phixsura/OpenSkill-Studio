"""User feedback collector — collect and analyze user feedback."""
from __future__ import annotations
import html
import time

_feedback: list[dict] = []


def submit_feedback(user_id: str, category: str, rating: int, comment: str) -> dict:
    if not 1 <= rating <= 5:
        return {"submitted": False, "error": "rating_must_be_1_to_5"}
    entry = {"user_id": user_id, "category": category, "rating": rating,
             "comment": html.escape(comment), "timestamp": time.time()}
    _feedback.append(entry)
    return {"submitted": True, **entry}


def analyze_feedback(category: str | None = None) -> dict:
    items = [f for f in _feedback if not category or f["category"] == category]
    if not items:
        return {"count": 0, "avg_rating": 0, "by_rating": {}, "nps": 0}
    ratings = [f["rating"] for f in items]
    by_rating = {str(r): ratings.count(r) for r in range(1, 6)}
    promoters = sum(1 for r in ratings if r >= 4)
    detractors = sum(1 for r in ratings if r <= 2)
    nps = round((promoters - detractors) / len(ratings) * 100)
    return {"count": len(items), "avg_rating": round(sum(ratings) / len(ratings), 1),
            "by_rating": by_rating, "nps": nps}


def clear_feedback() -> None:
    _feedback.clear()
