"""Content moderation engine — detect and filter harmful content."""
from __future__ import annotations
import re

BLOCKED_PATTERNS = [
    re.compile(r"\b(spam|scam|phishing)\b", re.IGNORECASE),
    re.compile(r"<script[\s>]", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
]
WARN_PATTERNS = [
    re.compile(r"\b(click here|act now|limited time)\b", re.IGNORECASE),
]


def moderate_text(text: str) -> dict:
    flags = []
    for p in BLOCKED_PATTERNS:
        if p.search(text):
            flags.append({"type": "blocked", "pattern": p.pattern})
    for p in WARN_PATTERNS:
        if p.search(text):
            flags.append({"type": "warning", "pattern": p.pattern})
    blocked = any(f["type"] == "blocked" for f in flags)
    return {"text_length": len(text), "flags": flags, "flag_count": len(flags),
            "blocked": blocked, "action": "reject" if blocked else "approve" if not flags else "review"}


def moderate_batch(texts: list[str]) -> dict:
    results = [moderate_text(t) for t in texts]
    rejected = sum(1 for r in results if r["action"] == "reject")
    reviewed = sum(1 for r in results if r["action"] == "review")
    approved = sum(1 for r in results if r["action"] == "approve")
    return {"total": len(results), "rejected": rejected, "review": reviewed,
            "approved": approved, "results": results}
