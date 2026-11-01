"""App review system — submit, moderate, and aggregate marketplace app reviews."""
from __future__ import annotations
import html


class AppReviewSystem:
    def __init__(self):
        self._reviews: dict[str, list[dict]] = {}

    def submit(self, *, app_id: str, user_id: str, rating: int,
                title: str = "", body: str = "") -> dict:
        rating = max(1, min(5, rating))
        review = {"user_id": user_id, "rating": rating,
                  "title": html.escape(title), "body": html.escape(body[:2000]),
                  "status": "published"}
        self._reviews.setdefault(app_id, []).append(review)
        return {"submitted": True, "rating": rating, "app_id": app_id}

    def get_reviews(self, app_id: str, *, limit: int = 20) -> list[dict]:
        return self._reviews.get(app_id, [])[:limit]

    def summary(self, app_id: str) -> dict:
        reviews = self._reviews.get(app_id, [])
        if not reviews:
            return {"app_id": app_id, "count": 0, "avg_rating": 0, "distribution": {}}
        total = len(reviews)
        avg = round(sum(r["rating"] for r in reviews) / total, 1)
        dist = {i: sum(1 for r in reviews if r["rating"] == i) for i in range(1, 6)}
        return {"app_id": app_id, "count": total, "avg_rating": avg,
                "avg_display": f"{avg} ⭐", "distribution": dist}
