"""App API Developer API Endpoint Scoring — composite health scores per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointScore:
    endpoint: str
    availability_score: float  # 0-100
    latency_score: float       # 0-100
    error_rate_score: float    # 0-100
    documentation_score: float # 0-100

    @property
    def composite_score(self) -> float:
        return round((self.availability_score * 0.35 + self.latency_score * 0.25 + self.error_rate_score * 0.25 + self.documentation_score * 0.15), 1)

    @property
    def grade(self) -> str:
        s = self.composite_score
        if s >= 90: return "A"
        if s >= 80: return "B"
        if s >= 70: return "C"
        if s >= 60: return "D"
        return "F"

class AppAPIDeveloperAPIApiEndpointScoring:
    def __init__(self) -> None:
        self._scores: dict[tuple[str, str], EndpointScore] = {}

    def score(self, installation_id: str, endpoint: str, availability: float, latency: float, error_rate: float, documentation: float) -> EndpointScore:
        if not installation_id: raise ValueError("installation_id is required")
        for v in (availability, latency, error_rate, documentation):
            if not 0 <= v <= 100: raise ValueError("scores must be 0-100")
        s = EndpointScore(endpoint=endpoint, availability_score=availability, latency_score=latency, error_rate_score=error_rate, documentation_score=documentation)
        self._scores[(installation_id, endpoint)] = s
        return s

    def get(self, installation_id: str, endpoint: str) -> EndpointScore | None:
        return self._scores.get((installation_id, endpoint))

    def ranked(self, installation_id: str) -> list[EndpointScore]:
        scores = [s for (inst, _), s in self._scores.items() if inst == installation_id]
        return sorted(scores, key=lambda s: s.composite_score, reverse=True)

    def failing(self, installation_id: str) -> list[EndpointScore]:
        return [s for (inst, _), s in self._scores.items() if inst == installation_id and s.grade in ("D", "F")]
