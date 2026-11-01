"""Review Moderation — automated and manual moderation for extension reviews.

Filters spam, profanity, and low-quality reviews with configurable rules,
appeal workflow, and moderator action tracking.
"""
from __future__ import annotations
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ModerationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    APPEALED = "appealed"


class RejectionReason(str, Enum):
    SPAM = "spam"
    PROFANITY = "profanity"
    OFF_TOPIC = "off_topic"
    LOW_QUALITY = "low_quality"
    MANIPULATION = "manipulation"
    PERSONAL_ATTACK = "personal_attack"


# Simple word filter (production would use ML)
BLOCKED_PATTERNS = [
    re.compile(r"\b(buy\s+now|click\s+here|free\s+money)\b", re.I),
    re.compile(r"(https?://\S+){3,}", re.I),  # 3+ URLs = spam
]

MIN_REVIEW_LENGTH = 10
MAX_REVIEW_LENGTH = 5000


@dataclass
class ReviewModeration:
    moderation_id: str
    review_id: str
    extension_id: str
    author_id: str
    content: str
    rating: int
    status: ModerationStatus = ModerationStatus.PENDING
    rejection_reason: RejectionReason | None = None
    moderator_id: str = ""
    appeal_text: str = ""
    auto_flags: list[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class ReviewModerationService:
    """Moderates extension reviews with auto-filtering and manual review."""

    def __init__(self):
        self._moderations: dict[str, ReviewModeration] = {}
        self._author_counts: dict[str, int] = {}

    def submit_review(self, review_id: str, extension_id: str,
                      author_id: str, content: str, rating: int) -> ReviewModeration:
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be 1-5")
        if len(content) < MIN_REVIEW_LENGTH:
            raise ValueError(f"Review too short (min {MIN_REVIEW_LENGTH} chars)")
        if len(content) > MAX_REVIEW_LENGTH:
            raise ValueError(f"Review too long (max {MAX_REVIEW_LENGTH} chars)")

        mod_id = f"mod_{secrets.token_urlsafe(10)}"
        mod = ReviewModeration(
            moderation_id=mod_id, review_id=review_id,
            extension_id=extension_id, author_id=author_id,
            content=content, rating=rating,
        )

        # Auto-moderation checks
        flags = self._auto_check(content, author_id)
        mod.auto_flags = flags
        if flags:
            mod.status = ModerationStatus.FLAGGED
        else:
            mod.status = ModerationStatus.APPROVED

        self._moderations[mod_id] = mod
        self._author_counts[author_id] = self._author_counts.get(author_id, 0) + 1
        return mod

    def _auto_check(self, content: str, author_id: str) -> list[str]:
        flags = []
        for pattern in BLOCKED_PATTERNS:
            if pattern.search(content):
                flags.append("spam_pattern")
                break
        if self._author_counts.get(author_id, 0) >= 10:
            flags.append("high_volume_reviewer")
        if content == content.upper() and len(content) > 20:
            flags.append("all_caps")
        return flags

    def moderate(self, moderation_id: str, moderator_id: str,
                 action: ModerationStatus,
                 reason: RejectionReason | None = None) -> bool:
        mod = self._moderations.get(moderation_id)
        if not mod:
            return False
        if moderator_id == mod.author_id:
            raise PermissionError("Cannot moderate own review")
        mod.status = action
        mod.moderator_id = moderator_id
        mod.rejection_reason = reason
        return True

    def appeal(self, moderation_id: str, author_id: str,
               appeal_text: str) -> bool:
        mod = self._moderations.get(moderation_id)
        if not mod or mod.author_id != author_id:
            return False
        if mod.status != ModerationStatus.REJECTED:
            return False
        mod.status = ModerationStatus.APPEALED
        mod.appeal_text = appeal_text
        return True

    def get_queue(self, status: ModerationStatus | None = None) -> list[ReviewModeration]:
        mods = list(self._moderations.values())
        if status:
            mods = [m for m in mods if m.status == status]
        return mods

    def get_stats(self) -> dict:
        mods = list(self._moderations.values())
        by_status = {}
        for s in ModerationStatus:
            by_status[s.value] = sum(1 for m in mods if m.status == s)
        return {"total": len(mods), "by_status": by_status}
