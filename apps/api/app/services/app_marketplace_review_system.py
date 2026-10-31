"""Review System — ratings, reviews, and moderation for marketplace extensions.

Developers and users can leave reviews with ratings. Reviews can be
flagged, moderated, and aggregated into extension scores.
"""
from __future__ import annotations
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class Review:
    review_id: str
    extension_id: str
    author_id: str
    rating: int  # 1-5
    title: str
    body: str
    created_at: str
    helpful_count: int = 0
    flagged: bool = False
    verified_install: bool = False


class ReviewSystem:
    """Manages extension reviews with moderation."""

    def __init__(self):
        self._reviews: dict[str, Review] = {}
        self._by_extension: dict[str, list[str]] = {}  # ext -> [review_ids]

    def submit_review(
        self, review_id: str, extension_id: str, author_id: str,
        rating: int, title: str, body: str, verified: bool = False,
    ) -> tuple[Review | None, str]:
        """Submit a review. Rating must be 1-5. One review per author per extension."""
        if not 1 <= rating <= 5:
            return None, "Rating must be between 1 and 5"

        # Check for duplicate
        existing = self._by_extension.get(extension_id, [])
        for rid in existing:
            if self._reviews[rid].author_id == author_id:
                return None, "You have already reviewed this extension"

        review = Review(
            review_id=review_id, extension_id=extension_id,
            author_id=author_id, rating=rating, title=title, body=body,
            created_at=datetime.now(timezone.utc).isoformat(),
            verified_install=verified,
        )
        self._reviews[review_id] = review
        self._by_extension.setdefault(extension_id, []).append(review_id)
        return review, "Review submitted"

    def get_reviews(self, extension_id: str, sort_by: str = "recent") -> list[Review]:
        """Get reviews for an extension, sorted by recent or helpful."""
        ids = self._by_extension.get(extension_id, [])
        reviews = [self._reviews[rid] for rid in ids if not self._reviews[rid].flagged]
        if sort_by == "helpful":
            reviews.sort(key=lambda r: r.helpful_count, reverse=True)
        else:
            reviews.sort(key=lambda r: r.created_at, reverse=True)
        return reviews

    def get_rating_summary(self, extension_id: str) -> dict:
        """Get aggregated rating summary."""
        reviews = self.get_reviews(extension_id)
        if not reviews:
            return {"average": 0.0, "count": 0, "distribution": {i: 0 for i in range(1, 6)}}
        dist = {i: 0 for i in range(1, 6)}
        for r in reviews:
            dist[r.rating] += 1
        avg = sum(r.rating for r in reviews) / len(reviews)
        return {"average": round(avg, 2), "count": len(reviews), "distribution": dist}

    def mark_helpful(self, review_id: str) -> bool:
        review = self._reviews.get(review_id)
        if review:
            review.helpful_count += 1
            return True
        return False

    def flag_review(self, review_id: str, reason: str = "") -> bool:
        """Flag a review for moderation."""
        review = self._reviews.get(review_id)
        if review:
            review.flagged = True
            return True
        return False

    def unflag_review(self, review_id: str) -> bool:
        review = self._reviews.get(review_id)
        if review:
            review.flagged = False
            return True
        return False
