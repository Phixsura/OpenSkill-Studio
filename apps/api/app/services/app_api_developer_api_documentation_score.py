"""App API Developer API Documentation Score — measure documentation quality."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DocumentationScore:
    endpoint_coverage_pct: float = 0.0
    example_coverage_pct: float = 0.0
    error_doc_coverage_pct: float = 0.0
    changelog_freshness_days: int = 0
    guide_count: int = 0

    @property
    def overall_score(self) -> float:
        return round((self.endpoint_coverage_pct + self.example_coverage_pct + self.error_doc_coverage_pct) / 3, 1)

    @property
    def grade(self) -> str:
        s = self.overall_score
        if s >= 90: return "A"
        if s >= 75: return "B"
        if s >= 60: return "C"
        return "D"

class AppAPIDeveloperAPIDocumentationScore:
    def __init__(self) -> None:
        self._scores: dict[str, DocumentationScore] = {}

    def update(self, installation_id: str, **kwargs) -> DocumentationScore:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._scores:
            self._scores[installation_id] = DocumentationScore()
        s = self._scores[installation_id]
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        return s

    def get(self, installation_id: str) -> DocumentationScore:
        return self._scores.get(installation_id, DocumentationScore())
