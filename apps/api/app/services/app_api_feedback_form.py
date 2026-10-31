"""App API Feedback Form — collect developer feedback.

Manages feedback collection:
- Submit feedback with rating
- Categorize feedback
- Calculate satisfaction scores
- Per-installation scoped feedback
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FeedbackEntry:
    """A developer feedback entry."""

    feedback_id: str
    submitter: str
    rating: int  # 1-5
    category: str
    message: str = ""


class AppAPIFeedbackForm:
    """Collect developer feedback."""

    def __init__(self) -> None:
        self._entries: dict[str, list[FeedbackEntry]] = {}

    def submit(
        self, installation_id: str, feedback_id: str, submitter: str,
        rating: int, category: str, message: str = "",
    ) -> FeedbackEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (1 <= rating <= 5):
            raise ValueError("rating must be 1-5")

        entry = FeedbackEntry(
            feedback_id=feedback_id, submitter=submitter,
            rating=rating, category=category, message=message,
        )
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def avg_rating(self, installation_id: str, category: str | None = None) -> float:
        entries = self._entries.get(installation_id, [])
        if category:
            entries = [e for e in entries if e.category == category]
        if not entries:
            return 0.0
        return round(sum(e.rating for e in entries) / len(entries), 1)

    def nps(self, installation_id: str) -> float:
        """Net Promoter Score: (promoters - detractors) / total * 100."""
        entries = self._entries.get(installation_id, [])
        if not entries:
            return 0.0
        promoters = sum(1 for e in entries if e.rating >= 4)
        detractors = sum(1 for e in entries if e.rating <= 2)
        return round((promoters - detractors) / len(entries) * 100, 1)

    def by_category(self, installation_id: str) -> dict[str, int]:
        cats: dict[str, int] = {}
        for e in self._entries.get(installation_id, []):
            cats[e.category] = cats.get(e.category, 0) + 1
        return cats

    def count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
