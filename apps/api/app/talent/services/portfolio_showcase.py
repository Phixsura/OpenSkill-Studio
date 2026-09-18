"""Portfolio showcase — curated work samples and project highlights.

Features:
  - Curated portfolio items (projects, work samples, case studies)
  - Visibility control per item (private, passport, public)
  - Ordering / pinning
  - Media attachments (links to assets)
  - Capability tagging per portfolio item
  - Portfolio completeness and quality scoring
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

PORTFOLIO_ITEM_TYPES = frozenset(
    {
        "project",
        "case_study",
        "work_sample",
        "publication",
        "presentation",
        "open_source",
        "certification_project",
        "commercial_deliverable",
        "research",
        "creative_work",
    }
)

PORTFOLIO_VISIBILITY = frozenset({"private", "passport_visible", "public"})


@dataclass(frozen=True, slots=True)
class PortfolioItem:
    """A curated portfolio entry."""

    id: str
    user_id: str
    item_type: str
    title: str
    description: str
    url: str | None
    image_url: str | None
    capability_ids: list[str]
    visibility: str
    pinned: bool
    sort_order: int
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PortfolioQuality:
    """Portfolio quality assessment."""

    total_items: int
    public_items: int
    items_with_urls: int
    items_with_images: int
    capability_coverage: int  # unique capabilities referenced
    has_commercial_work: bool
    has_open_source: bool
    quality_score: float  # 0-100
    suggestions: list[str]


class PortfolioShowcaseService:
    def assess_quality(self, items: list[PortfolioItem]) -> PortfolioQuality:
        """Assess portfolio quality and provide suggestions."""
        if not items:
            return PortfolioQuality(
                total_items=0,
                public_items=0,
                items_with_urls=0,
                items_with_images=0,
                capability_coverage=0,
                has_commercial_work=False,
                has_open_source=False,
                quality_score=0.0,
                suggestions=["Add your first portfolio item"],
            )

        public = sum(1 for i in items if i.visibility == "public")
        with_urls = sum(1 for i in items if i.url)
        with_images = sum(1 for i in items if i.image_url)
        all_caps = set()
        for i in items:
            all_caps.update(i.capability_ids)
        has_commercial = any(i.item_type == "commercial_deliverable" for i in items)
        has_oss = any(i.item_type == "open_source" for i in items)

        # Quality scoring
        score = 0.0
        score += min(len(items) / 5.0, 1.0) * 25  # Up to 25 for 5+ items
        score += min(public / 3.0, 1.0) * 20  # Up to 20 for 3+ public
        score += min(with_urls / max(len(items), 1), 1.0) * 15  # 15 for all having URLs
        score += min(with_images / max(len(items), 1), 1.0) * 10  # 10 for all having images
        score += min(len(all_caps) / 5.0, 1.0) * 15  # 15 for 5+ capabilities
        score += 10 if has_commercial else 0
        score += 5 if has_oss else 0

        suggestions = []
        if len(items) < 3:
            suggestions.append("Add more portfolio items (aim for 5+)")
        if public < 2:
            suggestions.append("Make at least 2 items public for employer visibility")
        if with_urls < len(items):
            suggestions.append("Add URLs/links to all portfolio items")
        if not has_commercial:
            suggestions.append("Add a commercial/professional project for credibility")
        if len(all_caps) < 3:
            suggestions.append("Tag items with more capabilities to show breadth")

        return PortfolioQuality(
            total_items=len(items),
            public_items=public,
            items_with_urls=with_urls,
            items_with_images=with_images,
            capability_coverage=len(all_caps),
            has_commercial_work=has_commercial,
            has_open_source=has_oss,
            quality_score=round(min(score, 100), 1),
            suggestions=suggestions,
        )

    def reorder_items(
        self,
        items: list[dict],
        new_order: list[str],
    ) -> list[dict]:
        """Reorder portfolio items by ID list."""
        by_id = {i["id"]: i for i in items}
        ordered = []
        for idx, item_id in enumerate(new_order):
            if item_id in by_id:
                by_id[item_id]["sort_order"] = idx
                ordered.append(by_id[item_id])
        # Append any items not in new_order at the end
        for item in items:
            if item.get("id", "") not in set(new_order):
                item["sort_order"] = len(ordered)
                ordered.append(item)
        return ordered
