"""App review response — developer response to app reviews."""

import html
import secrets
from datetime import datetime, timezone


def create_response(*, review_id: str, developer_id: str, body: str) -> dict:
    if len(body.strip()) < 10:
        return {"error": "Response must be at least 10 characters"}
    if len(body) > 2000:
        return {"error": "Response must be under 2000 characters"}
    return {
        "id": f"resp_{secrets.token_hex(6)}",
        "review_id": review_id, "developer_id": developer_id,
        "body": html.escape(body), "char_count": len(body),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_review_with_response(*, review: dict, response: dict | None = None) -> dict:
    return {
        "review": {
            "rating": review.get("rating", 0),
            "title": html.escape(review.get("title", "")),
            "body": html.escape(review.get("body", "")),
            "author": html.escape(review.get("author", "")),
        },
        "response": {
            "body": html.escape(response.get("body", "")),
            "responded_at": response.get("created_at", ""),
        } if response else None,
        "has_response": response is not None,
    }
