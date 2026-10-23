"""Content moderation queue — flag, review, and action on user content."""
from __future__ import annotations
import html
import re

BLOCKED_PATTERNS = [r"\b(spam|phishing|scam)\b"]


def moderate_content(items: list[dict]) -> dict:
    results = []
    counts = {"approved": 0, "flagged": 0, "rejected": 0}
    for item in items:
        text = html.escape(item.get("text", ""))
        item_id = item.get("id", "unknown")
        flags: list[str] = []
        if len(text) > 5000:
            flags.append("too_long")
        for pat in BLOCKED_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                flags.append("blocked_word")
                break
        if item.get("reported_count", 0) >= 3:
            flags.append("user_reports")
        if flags:
            status = "rejected" if "blocked_word" in flags else "flagged"
        else:
            status = "approved"
        counts[status] += 1
        results.append({"id": item_id, "status": status, "flags": flags,
                         "safe_text": text[:200]})
    return {"total": len(items), "counts": counts, "results": results,
            "queue_health": "clean" if counts["flagged"] == 0 and counts["rejected"] == 0 else "needs_review"}
