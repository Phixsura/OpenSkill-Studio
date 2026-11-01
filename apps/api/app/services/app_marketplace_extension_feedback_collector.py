"""Feedback Collector — collect and analyze user feedback for extensions.

Provides structured feedback collection with sentiment analysis,
categorization, and developer response tracking.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class FeedbackEntry:
    feedback_id: str
    extension_id: str
    user_id: str
    category: str  # bug, feature_request, question, praise, complaint
    message: str
    sentiment: str = ""  # positive, negative, neutral
    responded: bool = False
    response: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.sentiment:
            self.sentiment = self._detect_sentiment()

    def _detect_sentiment(self) -> str:
        positive = {"love", "great", "awesome", "excellent", "amazing", "thanks", "perfect", "helpful"}
        negative = {"bug", "broken", "crash", "hate", "terrible", "worst", "slow", "error", "fail"}
        words = set(self.message.lower().split())
        pos = len(words & positive)
        neg = len(words & negative)
        if pos > neg:
            return "positive"
        elif neg > pos:
            return "negative"
        return "neutral"


class FeedbackCollector:
    """Collects and analyzes extension feedback."""

    def __init__(self):
        self._feedback: dict[str, list[FeedbackEntry]] = defaultdict(list)

    def submit(self, entry: FeedbackEntry) -> FeedbackEntry:
        self._feedback[entry.extension_id].append(entry)
        return entry

    def respond(self, extension_id: str, feedback_id: str, response: str) -> bool:
        for entry in self._feedback.get(extension_id, []):
            if entry.feedback_id == feedback_id:
                entry.responded = True
                entry.response = response
                return True
        return False

    def get_feedback(self, extension_id: str, category: str | None = None,
                     sentiment: str | None = None, limit: int = 50) -> list[FeedbackEntry]:
        entries = self._feedback.get(extension_id, [])
        if category:
            entries = [e for e in entries if e.category == category]
        if sentiment:
            entries = [e for e in entries if e.sentiment == sentiment]
        return entries[-limit:]

    def get_sentiment_breakdown(self, extension_id: str) -> dict:
        entries = self._feedback.get(extension_id, [])
        breakdown = {"positive": 0, "negative": 0, "neutral": 0}
        for e in entries:
            breakdown[e.sentiment] = breakdown.get(e.sentiment, 0) + 1
        total = len(entries)
        return {
            "total": total, "breakdown": breakdown,
            "satisfaction_score": round(breakdown["positive"] / max(1, total) * 100, 1),
            "response_rate": round(sum(1 for e in entries if e.responded) / max(1, total) * 100, 1),
        }

    def get_top_categories(self, extension_id: str) -> list[dict]:
        entries = self._feedback.get(extension_id, [])
        counts: dict[str, int] = defaultdict(int)
        for e in entries:
            counts[e.category] += 1
        return sorted(
            [{"category": k, "count": v} for k, v in counts.items()],
            key=lambda x: x["count"], reverse=True,
        )
