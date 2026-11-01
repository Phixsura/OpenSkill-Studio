"""App API Developer Guide — manage step-by-step developer guides."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GuideStep:
    step_id: str
    title: str
    content: str

@dataclass
class DeveloperGuide:
    guide_id: str
    title: str
    category: str
    steps: list[GuideStep] = field(default_factory=list)
    view_count: int = 0

class AppAPIDeveloperGuide:
    def __init__(self) -> None:
        self._guides: dict[tuple[str, str], DeveloperGuide] = {}

    def create(self, installation_id: str, guide_id: str, title: str, category: str, steps: list[dict]) -> DeveloperGuide:
        if not installation_id: raise ValueError("installation_id is required")
        if not steps: raise ValueError("at least one step required")
        step_objs = [GuideStep(step_id=s["step_id"], title=s["title"], content=s.get("content", "")) for s in steps]
        g = DeveloperGuide(guide_id=guide_id, title=title, category=category, steps=step_objs)
        self._guides[(installation_id, guide_id)] = g
        return g

    def record_view(self, installation_id: str, guide_id: str) -> DeveloperGuide:
        g = self._get(installation_id, guide_id)
        g.view_count += 1
        return g

    def by_category(self, installation_id: str, category: str) -> list[DeveloperGuide]:
        return [g for (inst, _), g in self._guides.items() if inst == installation_id and g.category == category]

    def list_guides(self, installation_id: str) -> list[DeveloperGuide]:
        return [g for (inst, _), g in self._guides.items() if inst == installation_id]

    def _get(self, installation_id: str, guide_id: str) -> DeveloperGuide:
        g = self._guides.get((installation_id, guide_id))
        if g is None: raise KeyError(f"Guide {guide_id} not found")
        return g
