"""App API Developer Getting Started — structured getting started content."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GettingStartedSection:
    section_id: str
    title: str
    content: str
    code_example: str = ""
    language: str = ""
    order: int = 0

class AppAPIDeveloperGettingStarted:
    def __init__(self) -> None:
        self._sections: dict[tuple[str, str], GettingStartedSection] = {}

    def add_section(self, installation_id: str, section_id: str, title: str, content: str, code_example: str = "", language: str = "", order: int = 0) -> GettingStartedSection:
        if not installation_id: raise ValueError("installation_id is required")
        s = GettingStartedSection(section_id=section_id, title=title, content=content, code_example=code_example, language=language, order=order)
        self._sections[(installation_id, section_id)] = s
        return s

    def list_sections(self, installation_id: str) -> list[GettingStartedSection]:
        sections = [s for (inst, _), s in self._sections.items() if inst == installation_id]
        return sorted(sections, key=lambda s: s.order)

    def get_section(self, installation_id: str, section_id: str) -> GettingStartedSection:
        s = self._sections.get((installation_id, section_id))
        if s is None: raise KeyError(f"Section {section_id} not found")
        return s
