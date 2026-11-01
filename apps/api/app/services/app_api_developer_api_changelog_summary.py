"""App API Developer API Changelog Summary — aggregate changelog statistics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogSummary:
    total_versions: int = 0
    total_entries: int = 0
    breaking_changes: int = 0
    total_subscribers: int = 0
    total_reactions: int = 0
    total_comments: int = 0
    avg_entries_per_version: float = 0.0

class AppAPIDeveloperAPIChangelogSummary:
    def __init__(self) -> None:
        self._summaries: dict[str, ChangelogSummary] = {}

    def update(self, installation_id: str, **kwargs) -> ChangelogSummary:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._summaries:
            self._summaries[installation_id] = ChangelogSummary()
        s = self._summaries[installation_id]
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        return s

    def get(self, installation_id: str) -> ChangelogSummary:
        return self._summaries.get(installation_id, ChangelogSummary())
