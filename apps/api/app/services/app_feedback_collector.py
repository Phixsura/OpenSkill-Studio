"""App Feedback Collector — gather and analyze user feedback for marketplace apps.

Collects structured feedback from app users:
- Star ratings (1-5) with optional text
- Sentiment classification (positive, neutral, negative)
- Average rating computation
- Rating distribution histogram
- Recent feedback listing
- Feedback moderation (flag/hide)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class FeedbackStatus(str, Enum):
    VISIBLE = "visible"
    FLAGGED = "flagged"
    HIDDEN = "hidden"


@dataclass
class FeedbackEntry:
    """A single feedback submission."""

    feedback_id: str
    app_id: str
    user_id: str
    rating: int               # 1-5
    comment: str
    sentiment: Sentiment
    status: FeedbackStatus = FeedbackStatus.VISIBLE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class FeedbackSummary:
    """Aggregated feedback stats for an app."""

    app_id: str
    total_count: int
    avg_rating: float
    distribution: dict[int, int]   # rating → count
    sentiment_breakdown: dict[str, int]
    recent: list[FeedbackEntry]


def classify_sentiment(rating: int, comment: str) -> Sentiment:
    """Simple sentiment from rating + keywords."""
    if rating >= 4:
        return Sentiment.POSITIVE
    if rating <= 2:
        return Sentiment.NEGATIVE
    # Rating 3: check comment for hints
    neg_words = {"bug", "broken", "slow", "crash", "bad", "terrible", "awful"}
    pos_words = {"good", "nice", "okay", "decent", "fine", "works"}
    words = set(comment.lower().split())
    if words & neg_words:
        return Sentiment.NEGATIVE
    if words & pos_words:
        return Sentiment.POSITIVE
    return Sentiment.NEUTRAL


class AppFeedbackCollector:
    """Collect and query app feedback."""

    def __init__(self):
        self._feedback: dict[str, list[FeedbackEntry]] = {}
        self._next_id = 0

    def submit(self, app_id: str, user_id: str, rating: int,
               comment: str = "") -> FeedbackEntry:
        """Submit feedback. Rating must be 1-5."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        if not user_id:
            raise ValueError("user_id is required")

        self._next_id += 1
        sentiment = classify_sentiment(rating, comment)
        entry = FeedbackEntry(
            feedback_id=f"fb-{self._next_id}",
            app_id=app_id, user_id=user_id,
            rating=rating, comment=comment,
            sentiment=sentiment,
        )
        self._feedback.setdefault(app_id, []).append(entry)
        return entry

    def flag(self, app_id: str, feedback_id: str) -> bool:
        for fb in self._feedback.get(app_id, []):
            if fb.feedback_id == feedback_id:
                fb.status = FeedbackStatus.FLAGGED
                return True
        return False

    def hide(self, app_id: str, feedback_id: str) -> bool:
        for fb in self._feedback.get(app_id, []):
            if fb.feedback_id == feedback_id:
                fb.status = FeedbackStatus.HIDDEN
                return True
        return False

    def get_summary(self, app_id: str) -> FeedbackSummary:
        entries = [fb for fb in self._feedback.get(app_id, [])
                   if fb.status == FeedbackStatus.VISIBLE]
        total = len(entries)
        avg = sum(fb.rating for fb in entries) / total if total > 0 else 0.0
        dist = Counter(fb.rating for fb in entries)
        sent = Counter(fb.sentiment.value for fb in entries)

        return FeedbackSummary(
            app_id=app_id,
            total_count=total,
            avg_rating=round(avg, 2),
            distribution={r: dist.get(r, 0) for r in range(1, 6)},
            sentiment_breakdown=dict(sent),
            recent=sorted(entries, key=lambda f: f.created_at, reverse=True)[:5],
        )

    def get_feedback(self, app_id: str, limit: int = 20,
                     visible_only: bool = True) -> list[FeedbackEntry]:
        entries = self._feedback.get(app_id, [])
        if visible_only:
            entries = [fb for fb in entries if fb.status == FeedbackStatus.VISIBLE]
        return sorted(entries, key=lambda f: f.created_at, reverse=True)[:limit]

    def get_avg_rating(self, app_id: str) -> float:
        entries = [fb for fb in self._feedback.get(app_id, [])
                   if fb.status == FeedbackStatus.VISIBLE]
        if not entries:
            return 0.0
        return round(sum(fb.rating for fb in entries) / len(entries), 2)
