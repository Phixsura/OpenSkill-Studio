"""Content Moderation — automated and manual moderation for marketplace content.

Screens extension names, descriptions, screenshots, and reviews for
policy violations using keyword detection and manual review queues.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ModerationAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    FLAG = "flag"
    ESCALATE = "escalate"


class ContentType(str, Enum):
    NAME = "name"
    DESCRIPTION = "description"
    REVIEW = "review"
    SCREENSHOT = "screenshot"


BLOCKED_WORDS = {"spam", "scam", "hack", "malware", "phishing", "exploit", "crack", "pirate"}
FLAGGED_WORDS = {"free money", "guaranteed", "click here", "act now", "limited time"}


@dataclass
class ModerationResult:
    content_id: str
    content_type: ContentType
    action: ModerationAction
    reasons: list[str] = field(default_factory=list)
    confidence: float = 1.0
    moderator: str = "auto"
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class ContentModerationService:
    """Screens marketplace content for policy violations."""

    def __init__(self):
        self._results: dict[str, ModerationResult] = {}
        self._queue: list[str] = []  # content_ids pending manual review

    def screen(self, content_id: str, content_type: ContentType,
               text: str) -> ModerationResult:
        """Auto-screen content against policies."""
        text_lower = text.lower()
        reasons = []

        # Check blocked words
        for word in BLOCKED_WORDS:
            if word in text_lower:
                reasons.append(f"Blocked word: '{word}'")

        # Check flagged words
        flag_reasons = []
        for phrase in FLAGGED_WORDS:
            if phrase in text_lower:
                flag_reasons.append(f"Suspicious phrase: '{phrase}'")

        if reasons:
            action = ModerationAction.REJECT
        elif flag_reasons:
            action = ModerationAction.FLAG
            reasons = flag_reasons
            self._queue.append(content_id)
        else:
            action = ModerationAction.APPROVE

        confidence = 0.95 if action == ModerationAction.REJECT else 0.7 if action == ModerationAction.FLAG else 1.0
        result = ModerationResult(content_id, content_type, action, reasons, confidence)
        self._results[content_id] = result
        return result

    def manual_review(self, content_id: str, action: ModerationAction,
                      moderator: str, reason: str = "") -> bool:
        """Override auto moderation with manual decision."""
        result = self._results.get(content_id)
        if not result:
            return False
        result.action = action
        result.moderator = moderator
        result.confidence = 1.0
        if reason:
            result.reasons.append(f"Manual: {reason}")
        if content_id in self._queue:
            self._queue.remove(content_id)
        return True

    def get_result(self, content_id: str) -> ModerationResult | None:
        return self._results.get(content_id)

    def get_queue(self) -> list[str]:
        return list(self._queue)

    def get_stats(self) -> dict:
        results = list(self._results.values())
        by_action = {a.value: 0 for a in ModerationAction}
        for r in results:
            by_action[r.action.value] += 1
        return {
            "total_screened": len(results),
            "by_action": by_action,
            "pending_review": len(self._queue),
            "auto_rate": round(sum(1 for r in results if r.moderator == "auto") / max(1, len(results)) * 100, 1),
        }
