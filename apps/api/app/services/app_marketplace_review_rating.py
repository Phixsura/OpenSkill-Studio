"""Marketplace review/rating system — user reviews for apps."""

from collections import defaultdict
from datetime import UTC, datetime

_reviews: dict[str, list[dict]] = defaultdict(list)


def add_review(*, app_id: str, user_id: str, rating: int, comment: str = "") -> dict | None:
    """Add a review (1-5 stars). One review per user per app."""
    if not 1 <= rating <= 5:
        return None
    # Check duplicate
    existing = [r for r in _reviews[app_id] if r["user_id"] == user_id]
    if existing:
        return None
    review = {"app_id": app_id, "user_id": user_id, "rating": rating,
              "comment": comment, "created_at": datetime.now(UTC).isoformat()}
    _reviews[app_id].append(review)
    return review


def get_reviews(app_id: str, *, limit: int = 20) -> list[dict]:
    return _reviews.get(app_id, [])[-limit:]


def get_rating_summary(app_id: str) -> dict:
    reviews = _reviews.get(app_id, [])
    if not reviews:
        return {"average": 0, "count": 0, "distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}}
    dist = {i: sum(1 for r in reviews if r["rating"] == i) for i in range(1, 6)}
    avg = round(sum(r["rating"] for r in reviews) / len(reviews), 1)
    return {"average": avg, "count": len(reviews), "distribution": dist}
