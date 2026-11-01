"""App API Developer Experience Score — holistic DX quality measurement."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeveloperExperienceScore:
    # Documentation
    doc_coverage_pct: float = 0.0
    api_reference_complete: bool = False
    # Onboarding
    onboarding_completion_pct: float = 0.0
    avg_time_to_first_call_hours: float = 0.0
    # Reliability
    uptime_pct: float = 100.0
    avg_latency_ms: float = 0.0
    # Support
    avg_ticket_resolution_hours: float = 0.0
    open_tickets: int = 0
    # Community
    nps: float = 0.0
    active_developers: int = 0

    @property
    def dx_score(self) -> int:
        score = 0
        score += min(25, int(self.doc_coverage_pct / 4))
        score += min(20, int(self.onboarding_completion_pct / 5))
        score += min(20, 20 if self.uptime_pct >= 99.9 else int(self.uptime_pct - 80) if self.uptime_pct > 80 else 0)
        score += min(15, 15 if self.avg_ticket_resolution_hours < 4 else 10 if self.avg_ticket_resolution_hours < 24 else 5)
        score += min(20, int((self.nps + 100) / 10))
        return min(100, max(0, score))

    @property
    def dx_grade(self) -> str:
        s = self.dx_score
        if s >= 90: return "A"
        if s >= 80: return "B"
        if s >= 70: return "C"
        if s >= 60: return "D"
        return "F"

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScore:
    def __init__(self) -> None:
        self._scores: dict[str, DeveloperExperienceScore] = {}

    def update(self, installation_id: str, **kwargs) -> DeveloperExperienceScore:
        if not installation_id: raise ValueError("installation_id is required")
        s = DeveloperExperienceScore()
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._scores[installation_id] = s
        return s

    def get(self, installation_id: str) -> DeveloperExperienceScore:
        return self._scores.get(installation_id, DeveloperExperienceScore())
