"""Review card display — format individual review for display."""

import html
from datetime import datetime


def format_review_card(*, review: dict) -> dict:
    return {
        "review_id": review.get("review_id", ""),
        "author": html.escape(review.get("author", "Anonymous")),
        "avatar_initials": "".join(w[0].upper() for w in review.get("author", "A").split()[:2]),
        "rating": review.get("rating", 0),
        "stars": "★" * review.get("rating", 0) + "☆" * (5 - review.get("rating", 0)),
        "title": html.escape(review.get("title", "")),
        "body": html.escape(review.get("body", "")),
        "helpful_count": review.get("helpful_count", 0),
        "date_display": review.get("created_at", "")[:10],
        "has_response": review.get("developer_response") is not None,
        "developer_response": html.escape(review.get("developer_response", "")) if review.get("developer_response") else None,
    }
