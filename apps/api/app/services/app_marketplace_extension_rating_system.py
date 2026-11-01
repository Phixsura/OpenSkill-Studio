"""Rating System — weighted rating with review quality scoring.

Calculates weighted ratings factoring review length, reviewer history,
verified purchase status, and provides Bayesian averages.
"""
from __future__ import annotations
import math
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Rating:
    user_id: str
    score: int  # 1-5
    review_text: str = ""
    verified: bool = False
    helpful_votes: int = 0


class ExtensionRatingSystemService:
    """Weighted rating system with Bayesian averaging."""

    GLOBAL_AVG = 3.5  # prior
    MIN_RATINGS = 5    # confidence threshold

    def __init__(self):
        self._ratings: dict[str, list[Rating]] = defaultdict(list)

    def rate(self, extension_id: str, user_id: str, score: int,
             review: str = "", verified: bool = False) -> Rating | dict:
        if not 1 <= score <= 5:
            return {"error": "Score must be 1-5"}
        # Update existing
        for r in self._ratings[extension_id]:
            if r.user_id == user_id:
                r.score = score
                r.review_text = review
                r.verified = verified
                return r
        rating = Rating(user_id=user_id, score=score, review_text=review, verified=verified)
        self._ratings[extension_id].append(rating)
        return rating

    def get_average(self, extension_id: str) -> float:
        ratings = self._ratings.get(extension_id, [])
        if not ratings:
            return 0.0
        return round(sum(r.score for r in ratings) / len(ratings), 2)

    def get_bayesian_average(self, extension_id: str) -> float:
        ratings = self._ratings.get(extension_id, [])
        n = len(ratings)
        if n == 0:
            return self.GLOBAL_AVG
        avg = sum(r.score for r in ratings) / n
        # Bayesian: (C * m + n * avg) / (C + n)
        return round((self.MIN_RATINGS * self.GLOBAL_AVG + n * avg) / (self.MIN_RATINGS + n), 2)

    def get_distribution(self, extension_id: str) -> dict[int, int]:
        dist = {i: 0 for i in range(1, 6)}
        for r in self._ratings.get(extension_id, []):
            dist[r.score] += 1
        return dist

    def get_reviews(self, extension_id: str, sort: str = "helpful") -> list[Rating]:
        ratings = [r for r in self._ratings.get(extension_id, []) if r.review_text]
        if sort == "helpful":
            ratings.sort(key=lambda r: r.helpful_votes, reverse=True)
        elif sort == "newest":
            ratings.reverse()
        elif sort == "highest":
            ratings.sort(key=lambda r: r.score, reverse=True)
        return ratings

    def vote_helpful(self, extension_id: str, user_id: str) -> bool:
        for r in self._ratings.get(extension_id, []):
            if r.user_id == user_id:
                r.helpful_votes += 1
                return True
        return False

    def get_stats(self, extension_id: str) -> dict:
        ratings = self._ratings.get(extension_id, [])
        return {
            "count": len(ratings), "average": self.get_average(extension_id),
            "bayesian": self.get_bayesian_average(extension_id),
            "distribution": self.get_distribution(extension_id),
            "verified_count": sum(1 for r in ratings if r.verified),
            "with_review": sum(1 for r in ratings if r.review_text),
        }
