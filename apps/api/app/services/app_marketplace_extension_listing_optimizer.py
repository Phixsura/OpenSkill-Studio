"""Listing Optimizer — analyze and score extension marketplace listings.

Evaluates listing completeness, SEO quality, screenshot coverage,
description readability, and provides actionable improvement suggestions.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class ListingData:
    title: str = ""
    short_description: str = ""
    long_description: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    icon_url: str = ""
    demo_url: str = ""
    documentation_url: str = ""
    changelog: str = ""
    pricing_info: str = ""


@dataclass
class ListingScore:
    total: int
    max_score: int
    grade: str
    sections: dict[str, dict]
    suggestions: list[str]


class ListingOptimizerService:
    """Analyzes and scores marketplace listings for quality."""

    def analyze(self, listing: ListingData) -> ListingScore:
        sections: dict[str, dict] = {}
        suggestions: list[str] = []
        total = 0

        # Title (max 15)
        title_score = 0
        if listing.title:
            title_score += 5
            if 10 <= len(listing.title) <= 60:
                title_score += 5
            else:
                suggestions.append("Title should be 10-60 characters")
            if not listing.title.isupper():
                title_score += 5
            else:
                suggestions.append("Avoid ALL CAPS in title")
        else:
            suggestions.append("Add a title")
        sections["title"] = {"score": title_score, "max": 15}
        total += title_score

        # Description (max 25)
        desc_score = 0
        if listing.short_description:
            desc_score += 5
            if 50 <= len(listing.short_description) <= 160:
                desc_score += 5
            else:
                suggestions.append("Short description should be 50-160 characters")
        else:
            suggestions.append("Add a short description")
        if listing.long_description:
            desc_score += 5
            words = len(listing.long_description.split())
            if words >= 100:
                desc_score += 5
            else:
                suggestions.append("Long description should be 100+ words")
            if re.search(r"#{1,3}\s", listing.long_description):
                desc_score += 5
            else:
                suggestions.append("Use headings in long description for readability")
        else:
            suggestions.append("Add a detailed description")
        sections["description"] = {"score": desc_score, "max": 25}
        total += desc_score

        # Media (max 20)
        media_score = 0
        if listing.icon_url:
            media_score += 5
        else:
            suggestions.append("Add an icon")
        if listing.screenshots:
            media_score += 5
            if len(listing.screenshots) >= 3:
                media_score += 5
            else:
                suggestions.append("Add at least 3 screenshots")
            if len(listing.screenshots) >= 5:
                media_score += 5
        else:
            suggestions.append("Add screenshots")
        sections["media"] = {"score": media_score, "max": 20}
        total += media_score

        # Metadata (max 20)
        meta_score = 0
        if listing.category:
            meta_score += 5
        else:
            suggestions.append("Select a category")
        if listing.tags:
            meta_score += 5
            if len(listing.tags) >= 3:
                meta_score += 5
            else:
                suggestions.append("Add at least 3 tags")
        else:
            suggestions.append("Add tags for discoverability")
        if listing.pricing_info:
            meta_score += 5
        else:
            suggestions.append("Add pricing information")
        sections["metadata"] = {"score": meta_score, "max": 20}
        total += meta_score

        # Resources (max 20)
        res_score = 0
        if listing.demo_url:
            res_score += 5
        else:
            suggestions.append("Add a demo URL")
        if listing.documentation_url:
            res_score += 5
        else:
            suggestions.append("Add documentation link")
        if listing.changelog:
            res_score += 5
            if len(listing.changelog.split("\n")) >= 5:
                res_score += 5
            else:
                suggestions.append("Expand changelog with more entries")
        else:
            suggestions.append("Add a changelog")
        sections["resources"] = {"score": res_score, "max": 20}
        total += res_score

        max_score = 100
        if total >= 90:
            grade = "A"
        elif total >= 75:
            grade = "B"
        elif total >= 60:
            grade = "C"
        elif total >= 40:
            grade = "D"
        else:
            grade = "F"

        return ListingScore(total=total, max_score=max_score,
                            grade=grade, sections=sections,
                            suggestions=suggestions)
