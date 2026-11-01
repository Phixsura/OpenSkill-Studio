"""App API Developer Changelog AI Summary — AI-generated changelog summaries."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class AISummary:
    summary_id: str
    version: str
    summary: str
    key_points: list[str]
    generated: bool = True

class AppAPIDeveloperChangelogAISummary:
    def __init__(self) -> None:
        self._summaries: dict[tuple[str, str], AISummary] = {}

    def generate(self, installation_id: str, summary_id: str, version: str, summary: str, key_points: list[str]) -> AISummary:
        if not installation_id: raise ValueError("installation_id is required")
        if not summary.strip(): raise ValueError("summary cannot be empty")
        s = AISummary(summary_id=summary_id, version=version, summary=summary, key_points=key_points)
        self._summaries[(installation_id, summary_id)] = s
        return s

    def get_for_version(self, installation_id: str, version: str) -> AISummary | None:
        for (inst, _), s in self._summaries.items():
            if inst == installation_id and s.version == version:
                return s
        return None

    def list_summaries(self, installation_id: str) -> list[AISummary]:
        return [s for (inst, _), s in self._summaries.items() if inst == installation_id]
