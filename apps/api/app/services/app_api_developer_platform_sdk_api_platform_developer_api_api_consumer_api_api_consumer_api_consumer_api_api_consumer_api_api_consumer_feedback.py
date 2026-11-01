"""Consumer API Consumer Feedback — collect and manage consumer feedback."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class Feedback:
    feedback_id: str
    consumer_id: str
    rating: int  # 1-5
    category: str  # "api_quality", "documentation", "support", "pricing", "performance"
    comment: str = ""
    endpoint: str = ""
    created_at: datetime | None = None
    status: str = "new"  # "new", "reviewed", "resolved"

@dataclass
class FeedbackSummary:
    total_count: int
    average_rating: float
    by_category: dict[str, float]
    by_rating: dict[int, int]

VALID_CATEGORIES = {"api_quality", "documentation", "support", "pricing", "performance", "general"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerFeedback:
    def __init__(self) -> None:
        self._feedback: dict[tuple[str, str], Feedback] = {}

    def submit(self, installation_id: str, feedback: Feedback) -> Feedback:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (1 <= feedback.rating <= 5):
            raise ValueError("rating must be 1-5")
        if feedback.category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {feedback.category}")
        feedback.created_at = feedback.created_at or datetime.utcnow()
        feedback.status = "new"
        self._feedback[(installation_id, feedback.feedback_id)] = feedback
        log.info("feedback_submitted", installation_id=installation_id, consumer=feedback.consumer_id, rating=feedback.rating)
        return feedback

    def update_status(self, installation_id: str, feedback_id: str, status: str) -> Feedback:
        key = (installation_id, feedback_id)
        fb = self._feedback.get(key)
        if not fb:
            raise ValueError("Feedback not found")
        if status not in ("new", "reviewed", "resolved"):
            raise ValueError(f"Invalid status: {status}")
        fb.status = status
        return fb

    def get_summary(self, installation_id: str) -> FeedbackSummary:
        items = [f for (inst, _), f in self._feedback.items() if inst == installation_id]
        if not items:
            return FeedbackSummary(total_count=0, average_rating=0, by_category={}, by_rating={})
        avg = sum(f.rating for f in items) / len(items)
        by_cat: dict[str, list[int]] = {}
        by_rating: dict[int, int] = {}
        for f in items:
            by_cat.setdefault(f.category, []).append(f.rating)
            by_rating[f.rating] = by_rating.get(f.rating, 0) + 1
        cat_avg = {k: round(sum(v) / len(v), 1) for k, v in by_cat.items()}
        return FeedbackSummary(total_count=len(items), average_rating=round(avg, 1), by_category=cat_avg, by_rating=by_rating)

    def list_feedback(self, installation_id: str, consumer_id: str | None = None, status: str | None = None) -> list[Feedback]:
        items = [f for (inst, _), f in self._feedback.items() if inst == installation_id]
        if consumer_id:
            items = [f for f in items if f.consumer_id == consumer_id]
        if status:
            items = [f for f in items if f.status == status]
        return sorted(items, key=lambda f: f.created_at or datetime.min, reverse=True)
