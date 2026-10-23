"""App review — user review and rating system."""

import html
import secrets
from datetime import datetime, timezone


def create_review(*, app_id: str, user_id: str, rating: int,
                    title: str, body: str) -> dict:
    if not 1 <= rating <= 5:
        return {"error": "Rating must be 1-5"}
    return {"id": f"rev_{secrets.token_hex(6)}", "app_id": app_id, "user_id": user_id,
            "rating": rating, "title": html.escape(title), "body": html.escape(body),
            "helpful_count": 0, "created_at": datetime.now(timezone.utc).isoformat()}


def build_review_summary(*, reviews: list[dict]) -> dict:
    if not reviews:
        return {"avg_rating": 0, "total": 0, "distribution": {i: 0 for i in range(1, 6)}}
    dist = {i: 0 for i in range(1, 6)}
    for r in reviews:
        dist[r.get("rating", 5)] = dist.get(r.get("rating", 5), 0) + 1
    avg = round(sum(r.get("rating", 0) for r in reviews) / len(reviews), 1)
    return {"avg_rating": avg, "total": len(reviews), "distribution": dist,
            "stars_display": "★" * round(avg) + "☆" * (5 - round(avg)),
            "recent": sorted(reviews, key=lambda x: x.get("created_at", ""), reverse=True)[:5]}
