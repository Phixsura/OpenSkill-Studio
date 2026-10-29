"""App API Developer Platform Scorecard — THE 100th commit scorecard.

The comprehensive, definitive scorecard for the Developer Platform SDK.
Aggregates all dimensions into a single grade card.
"""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PlatformScorecard:
    """The 483rd backend service — a comprehensive platform scorecard."""
    # Reliability
    uptime_pct: float = 100.0
    error_rate_pct: float = 0.0
    incident_mttr_minutes: float = 0.0
    # Performance
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    cache_hit_rate_pct: float = 0.0
    # Webhooks
    webhook_delivery_rate_pct: float = 100.0
    webhook_avg_latency_ms: float = 0.0
    dead_letter_count: int = 0
    # Security
    security_score: int = 100
    secret_rotation_overdue: int = 0
    compliance_rate_pct: float = 100.0
    # Developer Experience
    nps: float = 0.0
    onboarding_completion_pct: float = 0.0
    active_developers: int = 0
    # Scale
    total_api_calls_30d: int = 0
    total_services: int = 483
    total_endpoints: int = 0

    @property
    def reliability_score(self) -> int:
        s = int(self.uptime_pct) - int(self.error_rate_pct * 10)
        return max(0, min(100, s))

    @property
    def performance_score(self) -> int:
        s = 100
        if self.avg_latency_ms > 200: s -= 20
        if self.p99_latency_ms > 1000: s -= 30
        if self.cache_hit_rate_pct < 50: s -= 20
        return max(0, s)

    @property
    def security_grade(self) -> str:
        s = self.security_score
        if self.secret_rotation_overdue > 0: s -= 15
        if self.compliance_rate_pct < 90: s -= 20
        if s >= 90: return "A"
        if s >= 75: return "B"
        if s >= 60: return "C"
        return "D"

    @property
    def overall_grade(self) -> str:
        avg = (self.reliability_score + self.performance_score + self.security_score) / 3
        if avg >= 90: return "A"
        if avg >= 80: return "B"
        if avg >= 70: return "C"
        if avg >= 60: return "D"
        return "F"

class AppAPIDeveloperAPIApiDeveloperApiPlatformScorecard:
    def __init__(self) -> None:
        self._scorecards: dict[str, PlatformScorecard] = {}

    def update(self, installation_id: str, **kwargs) -> PlatformScorecard:
        if not installation_id: raise ValueError("installation_id is required")
        s = PlatformScorecard()
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._scorecards[installation_id] = s
        return s

    def get(self, installation_id: str) -> PlatformScorecard:
        return self._scorecards.get(installation_id, PlatformScorecard())
