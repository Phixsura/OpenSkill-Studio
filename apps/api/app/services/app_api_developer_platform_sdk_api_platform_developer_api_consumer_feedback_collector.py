"""API Consumer Feedback Collector — collect and analyze consumer feedback on APIs."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class FeedbackEntry:
    feedback_id: str
    consumer_id: str
    endpoint: str
    rating: int  # 1-5
    category: str  # "bug", "feature", "docs", "performance", "other"
    comment: str = ""
    created_at: float = field(default_factory=time.time)

VALID_CATEGORIES = {"bug", "feature", "docs", "performance", "other"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerFeedbackCollector:
    def __init__(self) -> None:
        self._feedback: dict[str, list[FeedbackEntry]] = {}

    def submit(self, installation_id: str, entry: FeedbackEntry) -> FeedbackEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if not 1 <= entry.rating <= 5: raise ValueError("Rating must be 1-5")
        if entry.category not in VALID_CATEGORIES: raise ValueError(f"Invalid category: {entry.category}")
        if len(entry.comment) > 2000: entry.comment = entry.comment[:2000] + "...[TRUNCATED]"
        self._feedback.setdefault(installation_id, []).append(entry)
        return entry

    def average_rating(self, installation_id: str, endpoint: str | None = None) -> float:
        entries = self._feedback.get(installation_id, [])
        if endpoint: entries = [e for e in entries if e.endpoint == endpoint]
        if not entries: return 0.0
        return round(sum(e.rating for e in entries) / len(entries), 2)

    def by_category(self, installation_id: str) -> dict[str, int]:
        entries = self._feedback.get(installation_id, [])
        counts: dict[str, int] = {}
        for e in entries: counts[e.category] = counts.get(e.category, 0) + 1
        return counts

    def recent(self, installation_id: str, limit: int = 20) -> list[FeedbackEntry]:
        entries = self._feedback.get(installation_id, [])
        return list(reversed(entries[-limit:]))

    def low_rated_endpoints(self, installation_id: str, threshold: float = 3.0) -> list[tuple[str, float]]:
        entries = self._feedback.get(installation_id, [])
        ep_ratings: dict[str, list[int]] = {}
        for e in entries: ep_ratings.setdefault(e.endpoint, []).append(e.rating)
        return [(ep, round(sum(r) / len(r), 2)) for ep, r in ep_ratings.items() if sum(r) / len(r) < threshold]

    def count(self, installation_id: str) -> int:
        return len(self._feedback.get(installation_id, []))
