"""Consumer API Developer Portal — unified developer portal with getting started."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class GettingStartedStep:
    step_id: str
    title: str
    description: str
    code_example: str = ""
    order: int = 0


@dataclass
class PortalSection:
    section_id: str
    title: str
    content: str
    category: str = "guide"  # guide, reference, tutorial, faq
    order: int = 0


@dataclass
class DeveloperPortal:
    """Unified developer portal with onboarding, docs, and resources."""

    _sections: dict[str, PortalSection] = field(default_factory=dict)
    _getting_started: list[GettingStartedStep] = field(default_factory=list)
    _quicklinks: list[dict] = field(default_factory=list)

    def add_section(self, section: PortalSection) -> dict:
        if section.section_id in self._sections:
            raise ValueError(f"Section {section.section_id} already exists")
        self._sections[section.section_id] = section
        logger.info("portal_section_added", section_id=section.section_id)
        return {"section_id": section.section_id, "category": section.category}

    def add_getting_started_step(self, step: GettingStartedStep) -> dict:
        if any(s.step_id == step.step_id for s in self._getting_started):
            raise ValueError(f"Step {step.step_id} already exists")
        self._getting_started.append(step)
        self._getting_started.sort(key=lambda s: s.order)
        return {"step_id": step.step_id, "total_steps": len(self._getting_started)}

    def add_quicklink(self, title: str, url: str, icon: str = "") -> dict:
        self._quicklinks.append({"title": title, "url": url, "icon": icon})
        return {"title": title, "total": len(self._quicklinks)}

    def get_portal(self) -> dict:
        categories: dict[str, list[dict]] = {}
        for s in sorted(self._sections.values(), key=lambda x: x.order):
            cat = s.category
            categories.setdefault(cat, []).append({
                "section_id": s.section_id, "title": s.title,
            })
        steps = [
            {"step_id": s.step_id, "title": s.title,
             "description": s.description, "has_code": bool(s.code_example)}
            for s in self._getting_started
        ]
        return {
            "getting_started": steps,
            "categories": categories,
            "quicklinks": self._quicklinks,
            "total_sections": len(self._sections),
        }

    def get_section(self, section_id: str) -> dict | None:
        s = self._sections.get(section_id)
        if not s:
            return None
        return {"section_id": s.section_id, "title": s.title,
                "content": s.content, "category": s.category}

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        results = []
        for s in self._sections.values():
            if q in s.title.lower() or q in s.content.lower():
                results.append({"section_id": s.section_id, "title": s.title,
                                "category": s.category})
        return results

    def get_stats(self) -> dict:
        by_cat: dict[str, int] = {}
        for s in self._sections.values():
            by_cat[s.category] = by_cat.get(s.category, 0) + 1
        return {
            "total_sections": len(self._sections),
            "getting_started_steps": len(self._getting_started),
            "quicklinks": len(self._quicklinks),
            "by_category": by_cat,
        }
