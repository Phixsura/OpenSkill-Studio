"""App review response — allow developers to respond to user reviews."""

import html
import secrets
from datetime import datetime


def create_response(*, review_id: str, developer_id: str, message: str) -> dict:
    if len(message) < 10:
        return {"error": "Response must be at least 10 characters"}
    if len(message) > 2000:
        return {"error": "Response must be under 2000 characters"}
    return {
        "response_id": f"resp_{secrets.token_urlsafe(8)}",
        "review_id": review_id,
        "developer_id": developer_id,
        "message": html.escape(message),
        "created_at": datetime.utcnow().isoformat(),
        "visible": True,
    }


def get_response_stats(*, reviews: list[dict]) -> dict:
    total = len(reviews)
    responded = sum(1 for r in reviews if r.get("has_response"))
    unresponded_negative = sum(1 for r in reviews
                                if not r.get("has_response") and r.get("rating", 5) <= 2)
    response_rate = round(responded / max(total, 1) * 100, 1)
    return {
        "total_reviews": total,
        "responded": responded,
        "unresponded": total - responded,
        "unresponded_negative": unresponded_negative,
        "response_rate": response_rate,
    }
