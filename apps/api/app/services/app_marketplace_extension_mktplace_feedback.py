"""Marketplace Feedback — collect platform-level feedback from developers."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Feedback:
    feedback_id: str
    user_id: str
    category: str  # bug, feature, improvement, praise, other
    message: str
    rating: int = 0  # 1-5
    status: str = "new"  # new, reviewed, in_progress, resolved, wont_fix
    response: str = ""
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class MktplaceFeedbackService:
    CATEGORIES = {"bug", "feature", "improvement", "praise", "other"}

    def __init__(self):
        self._feedback: dict[str, Feedback] = {}
        self._counter = 0

    def submit(self, user_id: str, category: str, message: str,
               rating: int = 0) -> Feedback:
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")
        if rating and not (1 <= rating <= 5):
            raise ValueError("Rating must be 1-5")
        if not message.strip():
            raise ValueError("Message cannot be empty")
        self._counter += 1
        fb = Feedback(feedback_id=f"fb-{self._counter}", user_id=user_id,
                      category=category, message=message.strip(), rating=rating)
        self._feedback[fb.feedback_id] = fb
        return fb

    def respond(self, feedback_id: str, status: str, response: str = "") -> bool:
        fb = self._feedback.get(feedback_id)
        if not fb: return False
        fb.status = status
        fb.response = response
        return True

    def get_by_category(self, category: str) -> list[Feedback]:
        return [f for f in self._feedback.values() if f.category == category]

    def get_nps(self) -> float:
        rated = [f for f in self._feedback.values() if f.rating > 0]
        if not rated: return 0.0
        promoters = sum(1 for f in rated if f.rating >= 4)
        detractors = sum(1 for f in rated if f.rating <= 2)
        return round((promoters - detractors) / len(rated) * 100, 1)

    def get_stats(self) -> dict:
        by_cat: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for f in self._feedback.values():
            by_cat[f.category] = by_cat.get(f.category, 0) + 1
            by_status[f.status] = by_status.get(f.status, 0) + 1
        return {"total": len(self._feedback), "by_category": by_cat,
                "by_status": by_status, "nps": self.get_nps()}
