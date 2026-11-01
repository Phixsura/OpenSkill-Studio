"""App reviews page — complete reviews page with filters and stats."""

import html
from collections import Counter


def build_reviews_page(*, app_name: str, reviews: list[dict],
                         sort_by: str = "newest", filter_rating: int | None = None) -> dict:
    filtered = reviews
    if filter_rating:
        filtered = [r for r in reviews if r.get("rating") == filter_rating]
    if sort_by == "newest":
        filtered = sorted(filtered, key=lambda r: r.get("created_at", ""), reverse=True)
    elif sort_by == "highest":
        filtered = sorted(filtered, key=lambda r: r.get("rating", 0), reverse=True)
    elif sort_by == "lowest":
        filtered = sorted(filtered, key=lambda r: r.get("rating", 0))
    elif sort_by == "helpful":
        filtered = sorted(filtered, key=lambda r: r.get("helpful_count", 0), reverse=True)
    ratings = [r.get("rating", 0) for r in reviews]
    avg = round(sum(ratings) / max(len(ratings), 1), 1) if ratings else 0
    dist = Counter(ratings)
    items = [{
        "id": r.get("id", ""), "rating": r.get("rating", 0),
        "title": html.escape(r.get("title", "")), "body": html.escape(r.get("body", "")),
        "author": html.escape(r.get("author", "")),
        "helpful_count": r.get("helpful_count", 0),
        "created_at": r.get("created_at", ""),
        "has_response": r.get("has_response", False),
    } for r in filtered[:20]]
    return {"app_name": html.escape(app_name), "reviews": items,
            "total": len(reviews), "shown": len(items),
            "avg_rating": avg, "distribution": {i: dist.get(i, 0) for i in range(1, 6)},
            "stars": "★" * round(avg) + "☆" * (5 - round(avg)),
            "sort_by": sort_by, "filter_rating": filter_rating}
