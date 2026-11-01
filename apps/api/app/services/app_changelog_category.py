"""App Changelog Category — categorize changelog entries.

Manages changelog categories:
- Define categories (feature, fix, breaking, etc.)
- Assign entries to categories
- Count entries per category
- Per-installation scoped categories
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ChangelogCategory:
    """A changelog category."""

    category_id: str
    name: str
    emoji: str = ""
    sort_order: int = 0


@dataclass
class CategorizedEntry:
    """A changelog entry with category."""

    entry_id: str
    title: str
    category_id: str
    version: str


class AppChangelogCategory:
    """Categorize changelog entries."""

    def __init__(self) -> None:
        self._categories: dict[tuple[str, str], ChangelogCategory] = {}
        self._entries: dict[str, list[CategorizedEntry]] = {}

    def add_category(
        self, installation_id: str, category_id: str, name: str,
        emoji: str = "", sort_order: int = 0,
    ) -> ChangelogCategory:
        if not installation_id:
            raise ValueError("installation_id is required")
        cat = ChangelogCategory(
            category_id=category_id, name=name,
            emoji=emoji, sort_order=sort_order,
        )
        self._categories[(installation_id, category_id)] = cat
        return cat

    def add_entry(
        self, installation_id: str, entry_id: str, title: str,
        category_id: str, version: str,
    ) -> CategorizedEntry:
        if (installation_id, category_id) not in self._categories:
            raise KeyError(f"Category {category_id} not found")

        entry = CategorizedEntry(
            entry_id=entry_id, title=title,
            category_id=category_id, version=version,
        )
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def entries_by_category(self, installation_id: str, category_id: str) -> list[CategorizedEntry]:
        return [
            e for e in self._entries.get(installation_id, [])
            if e.category_id == category_id
        ]

    def category_counts(self, installation_id: str) -> list[dict]:
        cats = [c for (inst, _), c in self._categories.items() if inst == installation_id]
        cats.sort(key=lambda c: c.sort_order)
        entries = self._entries.get(installation_id, [])
        return [
            {"category": c.name, "emoji": c.emoji,
             "count": sum(1 for e in entries if e.category_id == c.category_id)}
            for c in cats
        ]

    def list_categories(self, installation_id: str) -> list[ChangelogCategory]:
        cats = [c for (inst, _), c in self._categories.items() if inst == installation_id]
        return sorted(cats, key=lambda c: c.sort_order)
