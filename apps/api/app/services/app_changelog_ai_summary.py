"""App Changelog AI Summary — generate AI-style summaries from changelog entries.

Generates concise summaries from multiple changelog entries:
- Aggregate entries into a single summary
- Highlight key changes by impact
- Group by category with counts
- Per-installation scoped summaries
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SummaryEntry:
    """An entry to summarize."""

    title: str
    category: str
    breaking: bool = False


@dataclass
class AISummary:
    """A generated summary."""

    version: str
    headline: str
    bullet_points: list[str]
    breaking_count: int
    category_counts: dict[str, int]
    total_changes: int


class AppChangelogAISummary:
    """Generate summaries from changelog entries."""

    def __init__(self) -> None:
        pass

    def summarize(
        self,
        version: str,
        entries: list[SummaryEntry],
    ) -> AISummary:
        """Generate a summary from entries."""
        if not version:
            raise ValueError("version is required")
        if not entries:
            raise ValueError("at least one entry required")

        # Category counts
        cat_counts: dict[str, int] = {}
        for e in entries:
            cat_counts[e.category] = cat_counts.get(e.category, 0) + 1

        breaking = [e for e in entries if e.breaking]

        # Generate headline
        top_cat = max(cat_counts, key=cat_counts.get) if cat_counts else "changes"
        headline = f"v{version}: {len(entries)} changes"
        if breaking:
            headline += f" ({len(breaking)} breaking)"

        # Generate bullet points
        bullets: list[str] = []
        # Breaking changes first
        for e in breaking:
            bullets.append(f"⚠ BREAKING: {e.title}")

        # Top entries by category
        seen_cats: set[str] = set()
        for e in entries:
            if not e.breaking and e.category not in seen_cats:
                count = cat_counts[e.category]
                if count > 1:
                    bullets.append(f"{e.title} (+{count - 1} more {e.category})")
                else:
                    bullets.append(e.title)
                seen_cats.add(e.category)

        return AISummary(
            version=version,
            headline=headline,
            bullet_points=bullets[:10],  # cap at 10
            breaking_count=len(breaking),
            category_counts=cat_counts,
            total_changes=len(entries),
        )
