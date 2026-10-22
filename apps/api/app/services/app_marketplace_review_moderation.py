"""Review moderation — flag, filter, auto-moderate reviews."""

import re

PROFANITY_PATTERNS = [r"\bspam\b", r"\bscam\b", r"\bfake\b"]
MIN_REVIEW_LENGTH = 10
MAX_REVIEW_LENGTH = 5000


def moderate_review(*, text: str, rating: int, reviewer_id: str, app_developer_id: str) -> dict:
    flags = []
    if len(text) < MIN_REVIEW_LENGTH:
        flags.append({"type": "too_short", "severity": "warn"})
    if len(text) > MAX_REVIEW_LENGTH:
        flags.append({"type": "too_long", "severity": "reject"})
    for pat in PROFANITY_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            flags.append({"type": "flagged_content", "severity": "review", "match": pat})
    if reviewer_id == app_developer_id:
        flags.append({"type": "self_review", "severity": "reject"})
    if rating < 1 or rating > 5:
        flags.append({"type": "invalid_rating", "severity": "reject"})
    has_reject = any(f["severity"] == "reject" for f in flags)
    needs_review = any(f["severity"] == "review" for f in flags)
    return {
        "status": "rejected" if has_reject else "pending_review" if needs_review else "approved",
        "flags": flags,
        "auto_moderated": not needs_review,
    }


def filter_reviews(*, reviews: list[dict], min_rating: int | None = None,
                     verified_only: bool = False) -> list[dict]:
    result = reviews
    if min_rating is not None:
        result = [r for r in result if r.get("rating", 0) >= min_rating]
    if verified_only:
        result = [r for r in result if r.get("verified_purchase")]
    return result
