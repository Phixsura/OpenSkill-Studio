"""App API Developer Feedback Collector — collect and analyze developer feedback."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class FeedbackItem:
    feedback_id: str
    developer_id: str
    category: str  # "bug", "feature", "improvement", "documentation", "other"
    rating: int  # 1-5
    comment: str
    status: str = "open"  # "open", "acknowledged", "resolved"
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperAPIDeveloperFeedbackCollector:
    def __init__(self) -> None:
        self._feedback: dict[tuple[str, str], FeedbackItem] = {}

    def submit(self, installation_id: str, feedback_id: str, developer_id: str, category: str, rating: int, comment: str) -> FeedbackItem:
        if not installation_id: raise ValueError("installation_id is required")
        if category not in ("bug", "feature", "improvement", "documentation", "other"): raise ValueError("invalid category")
        if not 1 <= rating <= 5: raise ValueError("rating must be 1-5")
        key = (installation_id, feedback_id)
        if key in self._feedback: raise ValueError(f"Feedback {feedback_id} exists")
        f = FeedbackItem(feedback_id=feedback_id, developer_id=developer_id, category=category, rating=rating, comment=comment)
        self._feedback[key] = f
        return f

    def update_status(self, installation_id: str, feedback_id: str, status: str) -> FeedbackItem:
        if status not in ("open", "acknowledged", "resolved"): raise ValueError("invalid status")
        key = (installation_id, feedback_id)
        f = self._feedback.get(key)
        if f is None: raise KeyError(f"Feedback {feedback_id} not found")
        f.status = status
        return f

    def avg_rating(self, installation_id: str) -> float:
        items = [f for (inst, _), f in self._feedback.items() if inst == installation_id]
        if not items: return 0.0
        return round(sum(f.rating for f in items) / len(items), 1)

    def by_category(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), f in self._feedback.items():
            if inst == installation_id: counts[f.category] = counts.get(f.category, 0) + 1
        return counts

    def open_feedback(self, installation_id: str) -> list[FeedbackItem]:
        return [f for (inst, _), f in self._feedback.items() if inst == installation_id and f.status == "open"]
