"""Review moderation — automated and manual review content moderation."""

import re


BLOCKED_PATTERNS = [
    re.compile(r"\b(spam|scam|fake)\b", re.IGNORECASE),
    re.compile(r"https?://[^\s]+\.(ru|cn|xyz)/", re.IGNORECASE),
]

PROFANITY_WORDS = {"damn", "hell"}  # minimal set for demo


def moderate_review(*, text: str, rating: int, reviewer_id: str) -> dict:
    flags = []
    for pat in BLOCKED_PATTERNS:
        if pat.search(text):
            flags.append({"type": "blocked_pattern", "detail": pat.pattern})
    words = set(text.lower().split())
    profanity_found = words & PROFANITY_WORDS
    if profanity_found:
        flags.append({"type": "profanity", "detail": ", ".join(sorted(profanity_found))})
    if rating == 1 and len(text) < 20:
        flags.append({"type": "low_effort", "detail": "1-star with very short text"})
    if len(text) > 5000:
        flags.append({"type": "too_long", "detail": f"Text length {len(text)} exceeds 5000"})
    action = "approve" if not flags else ("reject" if any(f["type"] == "blocked_pattern" for f in flags) else "review")
    return {"action": action, "flags": flags, "flag_count": len(flags),
            "reviewer_id": reviewer_id, "auto_moderated": True}


def bulk_moderate(*, reviews: list[dict]) -> dict:
    results = [moderate_review(text=r["text"], rating=r["rating"], reviewer_id=r["id"]) for r in reviews]
    return {
        "total": len(results),
        "approved": sum(1 for r in results if r["action"] == "approve"),
        "flagged": sum(1 for r in results if r["action"] == "review"),
        "rejected": sum(1 for r in results if r["action"] == "reject"),
    }
