"""Consumer API Access Review — periodic access review with attestation."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

REVIEW_STATUSES = ("pending", "approved", "revoked", "deferred")


@dataclass
class AccessEntry:
    entry_id: str
    consumer_id: str
    resource: str
    permission: str
    granted_at: str = ""
    last_used: str = ""


@dataclass
class ReviewDecision:
    entry_id: str
    decision: str
    reviewer: str
    reason: str = ""
    decided_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AccessReview:
    review_id: str
    period: str
    entries: list[AccessEntry] = field(default_factory=list)
    decisions: dict[str, ReviewDecision] = field(default_factory=dict)
    status: str = "open"  # open, completed


@dataclass
class AccessReviewManager:
    """Manage periodic access reviews with attestation tracking."""

    _reviews: dict[str, AccessReview] = field(default_factory=dict)

    def create_review(self, review_id: str, period: str,
                      entries: list[AccessEntry]) -> dict:
        if review_id in self._reviews:
            raise ValueError(f"Review {review_id} already exists")
        if not entries:
            raise ValueError("At least one entry required")
        review = AccessReview(review_id=review_id, period=period, entries=entries)
        self._reviews[review_id] = review
        logger.info("access_review_created", review_id=review_id, entries=len(entries))
        return {"review_id": review_id, "entries": len(entries), "status": "open"}

    def decide(self, review_id: str, entry_id: str, decision: str,
               reviewer: str, reason: str = "") -> dict:
        review = self._reviews.get(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
        if decision not in REVIEW_STATUSES:
            raise ValueError(f"Invalid decision: {decision}")
        if review.status == "completed":
            raise ValueError("Review already completed")
        valid_ids = {e.entry_id for e in review.entries}
        if entry_id not in valid_ids:
            raise ValueError(f"Entry {entry_id} not in review")
        review.decisions[entry_id] = ReviewDecision(
            entry_id=entry_id, decision=decision,
            reviewer=reviewer, reason=reason,
        )
        return {"entry_id": entry_id, "decision": decision, "reviewer": reviewer}

    def complete(self, review_id: str) -> dict:
        review = self._reviews.get(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
        undecided = [e for e in review.entries if e.entry_id not in review.decisions]
        if undecided:
            return {"completed": False, "undecided": len(undecided)}
        review.status = "completed"
        revoked = sum(1 for d in review.decisions.values() if d.decision == "revoked")
        return {"completed": True, "revoked": revoked,
                "approved": len(review.decisions) - revoked}

    def get_progress(self, review_id: str) -> dict:
        review = self._reviews.get(review_id)
        if not review:
            return {"error": "not_found"}
        total = len(review.entries)
        decided = len(review.decisions)
        return {
            "review_id": review_id, "status": review.status,
            "total": total, "decided": decided,
            "remaining": total - decided,
            "progress_pct": round(decided / total * 100, 1) if total > 0 else 0,
        }

    def get_decisions(self, review_id: str) -> list[dict]:
        review = self._reviews.get(review_id)
        if not review:
            return []
        results = []
        for entry in review.entries:
            decision = review.decisions.get(entry.entry_id)
            results.append({
                "entry_id": entry.entry_id, "consumer_id": entry.consumer_id,
                "resource": entry.resource, "permission": entry.permission,
                "decision": decision.decision if decision else "pending",
                "reviewer": decision.reviewer if decision else None,
            })
        return results

    def list_reviews(self) -> list[dict]:
        return [self.get_progress(rid) for rid in self._reviews]

    def get_stats(self) -> dict:
        reviews = list(self._reviews.values())
        total_entries = sum(len(r.entries) for r in reviews)
        total_revoked = sum(
            sum(1 for d in r.decisions.values() if d.decision == "revoked")
            for r in reviews
        )
        return {
            "total_reviews": len(reviews),
            "open": sum(1 for r in reviews if r.status == "open"),
            "completed": sum(1 for r in reviews if r.status == "completed"),
            "total_entries_reviewed": total_entries,
            "total_revoked": total_revoked,
        }
