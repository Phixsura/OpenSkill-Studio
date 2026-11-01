"""Marketplace Home — curated homepage for the extension marketplace.

Aggregates featured extensions, trending, new arrivals, top categories,
and personalized recommendations into a single homepage feed.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class HomeSection:
    section_id: str
    title: str
    section_type: str  # featured, trending, new, category, recommended
    items: list[dict] = field(default_factory=list)
    order: int = 0


class MarketplaceHomeService:
    """Curates the marketplace homepage."""

    def __init__(self):
        self._sections: list[HomeSection] = []
        self._featured: list[dict] = []

    def add_section(self, section_id: str, title: str, section_type: str,
                    items: list[dict], order: int = 0) -> HomeSection:
        section = HomeSection(section_id=section_id, title=title,
                              section_type=section_type, items=items, order=order)
        self._sections.append(section)
        self._sections.sort(key=lambda s: s.order)
        return section

    def set_featured(self, items: list[dict]) -> None:
        self._featured = items

    def get_homepage(self, user_id: str | None = None) -> dict:
        return {
            "featured": self._featured,
            "sections": [
                {"id": s.section_id, "title": s.title, "type": s.section_type,
                 "items": s.items[:12]}
                for s in self._sections
            ],
        }

    def get_section(self, section_id: str) -> HomeSection | None:
        return next((s for s in self._sections if s.section_id == section_id), None)

    def reorder(self, section_ids: list[str]) -> None:
        order_map = {sid: i for i, sid in enumerate(section_ids)}
        for s in self._sections:
            if s.section_id in order_map:
                s.order = order_map[s.section_id]
        self._sections.sort(key=lambda s: s.order)
