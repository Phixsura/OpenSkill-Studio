"""App review page — marketplace review submission and display."""

import html
import secrets
from datetime import datetime, timezone


def build_review_form(*, app_name: str, existing_review: dict | None = None) -> dict:
    return {
        "app_name": html.escape(app_name),
        "is_edit": existing_review is not None,
        "current_rating": existing_review.get("rating", 0) if existing_review else 0,
        "current_title": html.escape(existing_review.get("title", "")) if existing_review else "",
        "current_body": html.escape(existing_review.get("body", "")) if existing_review else "",
        "rating_labels": {1: "Terrible", 2: "Poor", 3: "Average", 4: "Good", 5: "Excellent"},
    }


def submit_review(*, app_id: str, user_id: str, rating: int,
                    title: str, body: str) -> dict:
    if not 1 <= rating <= 5:
        return {"error": "Rating must be 1-5"}
    if len(title.strip()) < 3:
        return {"error": "Title must be at least 3 characters"}
    return {
        "review_id": f"rev_{secrets.token_hex(6)}",
        "app_id": app_id, "user_id": user_id,
        "rating": rating, "title": html.escape(title),
        "body": html.escape(body),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "published",
    }
