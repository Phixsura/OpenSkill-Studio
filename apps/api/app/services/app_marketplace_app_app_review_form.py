"""Review form — validate and structure app review submissions."""

import html
import secrets
from datetime import datetime


def validate_review(*, rating: int, title: str, body: str, user_id: str) -> dict:
    errors = []
    if not 1 <= rating <= 5:
        errors.append("Rating must be 1-5")
    if len(title) < 5:
        errors.append("Title must be at least 5 characters")
    if len(title) > 100:
        errors.append("Title must be under 100 characters")
    if len(body) < 20:
        errors.append("Review must be at least 20 characters")
    if len(body) > 5000:
        errors.append("Review must be under 5000 characters")
    if errors:
        return {"valid": False, "errors": errors}
    return {
        "valid": True,
        "review": {
            "review_id": f"rev_{secrets.token_urlsafe(8)}",
            "rating": rating,
            "title": html.escape(title),
            "body": html.escape(body),
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "helpful_count": 0,
        },
    }
