"""App review moderation — moderate user reviews before publishing."""
from __future__ import annotations
import html
import re

BLOCKED_WORDS = ["spam", "scam", "fake", "hack"]


def moderate_review(review: dict) -> dict:
    text = review.get("body", "")
    rating = review.get("rating", 0)
    flags = []
    for word in BLOCKED_WORDS:
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            flags.append(f"blocked_word:{word}")
    if len(text) < 10:
        flags.append("too_short")
    if rating < 1 or rating > 5:
        flags.append("invalid_rating")
    if len(text) > 5000:
        flags.append("too_long")
    status = "rejected" if any("blocked_word" in f for f in flags) else \
             "flagged" if flags else "approved"
    return {"status": status, "flags": flags,
            "safe_body": html.escape(text[:2000]),
            "rating": max(1, min(5, rating))}


def moderation_stats(reviews: list[dict]) -> dict:
    results = [moderate_review(r) for r in reviews]
    by_status = {"approved": 0, "flagged": 0, "rejected": 0}
    for r in results:
        by_status[r["status"]] += 1
    return {"total": len(results), "by_status": by_status,
            "approval_rate": round(by_status["approved"] / max(len(results), 1) * 100)}
