"""Recommendation Engine — suggest extensions based on usage and context.

Generates personalized extension recommendations using collaborative
filtering (orgs that use X also use Y) and content-based matching.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Recommendation:
    extension_id: str
    score: float
    reason: str


class RecommendationEngine:
    """Generates extension recommendations for organizations."""

    def __init__(self):
        self._installs: dict[str, set[str]] = defaultdict(set)  # org -> {ext_ids}
        self._ext_tags: dict[str, set[str]] = defaultdict(set)  # ext -> {tags}
        self._ext_category: dict[str, str] = {}

    def record_install(self, org_id: str, extension_id: str) -> None:
        self._installs[org_id].add(extension_id)

    def set_extension_metadata(self, extension_id: str, tags: list[str],
                                category: str = "") -> None:
        self._ext_tags[extension_id] = set(tags)
        if category:
            self._ext_category[extension_id] = category

    def collaborative_filter(self, org_id: str, limit: int = 10) -> list[Recommendation]:
        """Recommend based on what similar orgs use."""
        my_exts = self._installs.get(org_id, set())
        if not my_exts:
            return []

        # Find orgs with overlap
        scores: dict[str, float] = defaultdict(float)
        for other_org, other_exts in self._installs.items():
            if other_org == org_id:
                continue
            overlap = len(my_exts & other_exts)
            if overlap == 0:
                continue
            similarity = overlap / len(my_exts | other_exts)
            for ext in other_exts - my_exts:
                scores[ext] += similarity

        recs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [Recommendation(ext, round(score, 3), "Similar orgs also use this")
                for ext, score in recs]

    def content_based(self, org_id: str, limit: int = 10) -> list[Recommendation]:
        """Recommend based on tag similarity to installed extensions."""
        my_exts = self._installs.get(org_id, set())
        if not my_exts:
            return []

        my_tags: set[str] = set()
        for ext in my_exts:
            my_tags |= self._ext_tags.get(ext, set())

        scores: dict[str, float] = {}
        for ext_id, tags in self._ext_tags.items():
            if ext_id in my_exts:
                continue
            overlap = len(my_tags & tags)
            if overlap > 0:
                scores[ext_id] = overlap / len(my_tags | tags)

        recs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [Recommendation(ext, round(score, 3), "Matches your interests")
                for ext, score in recs]

    def get_recommendations(self, org_id: str, limit: int = 10) -> list[Recommendation]:
        """Combined recommendations from all strategies."""
        collab = {r.extension_id: r for r in self.collaborative_filter(org_id, limit)}
        content = {r.extension_id: r for r in self.content_based(org_id, limit)}

        combined: dict[str, float] = {}
        reasons: dict[str, str] = {}
        for ext_id, rec in collab.items():
            combined[ext_id] = combined.get(ext_id, 0) + rec.score * 0.6
            reasons[ext_id] = rec.reason
        for ext_id, rec in content.items():
            combined[ext_id] = combined.get(ext_id, 0) + rec.score * 0.4
            reasons.setdefault(ext_id, rec.reason)

        sorted_recs = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [Recommendation(ext, round(score, 3), reasons.get(ext, ""))
                for ext, score in sorted_recs]

    def get_popular(self, limit: int = 10, exclude_org: str = "") -> list[str]:
        """Get most installed extensions."""
        counts: dict[str, int] = defaultdict(int)
        excluded = self._installs.get(exclude_org, set())
        for org_exts in self._installs.values():
            for ext in org_exts:
                if ext not in excluded:
                    counts[ext] += 1
        return [ext for ext, _ in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]]
