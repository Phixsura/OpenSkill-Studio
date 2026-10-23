"""Feedback widget — embeddable feedback collection for any page."""
from __future__ import annotations
import html

REACTION_TYPES = {
    "love": {"emoji": "😍", "label": "Love it"},
    "like": {"emoji": "👍", "label": "Good"},
    "meh": {"emoji": "😐", "label": "OK"},
    "dislike": {"emoji": "👎", "label": "Needs work"},
}


def collect_feedback(*, page: str, reaction: str, comment: str = "",
                       user_id: str = "") -> dict:
    if reaction not in REACTION_TYPES:
        return {"error": f"Invalid reaction: {reaction}"}
    return {"page": page, "reaction": reaction,
            "emoji": REACTION_TYPES[reaction]["emoji"],
            "comment": html.escape(comment[:500]),
            "user_id": user_id, "collected": True}


def summarize_feedback(feedbacks: list[dict]) -> dict:
    counts: dict[str, int] = {k: 0 for k in REACTION_TYPES}
    for f in feedbacks:
        r = f.get("reaction", "")
        if r in counts:
            counts[r] += 1
    total = len(feedbacks)
    positive = counts.get("love", 0) + counts.get("like", 0)
    satisfaction = round(positive / max(total, 1) * 100)
    return {"total": total, "counts": counts, "satisfaction_pct": satisfaction,
            "top_reaction": max(counts, key=counts.get) if total else None}
