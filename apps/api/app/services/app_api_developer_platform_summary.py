"""App API Developer Platform Summary — the ultimate platform summary service.

The final capstone — a single service that summarizes the entire developer platform:
- Developer counts and engagement
- API health and performance
- Webhook delivery stats
- Documentation and onboarding coverage
"""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PlatformSummary:
    # Developers
    total_developers: int = 0
    active_developers_30d: int = 0
    # API
    total_api_calls_30d: int = 0
    api_error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    # Webhooks
    webhook_success_rate: float = 100.0
    webhook_destinations: int = 0
    # Platform
    documentation_coverage_pct: float = 0.0
    onboarding_completion_pct: float = 0.0
    developer_satisfaction: float = 0.0
    open_incidents: int = 0
    open_support_tickets: int = 0

class AppAPIDeveloperPlatformSummary:
    def __init__(self) -> None:
        self._summaries: dict[str, PlatformSummary] = {}

    def update(self, installation_id: str, **kwargs) -> PlatformSummary:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._summaries:
            self._summaries[installation_id] = PlatformSummary()
        s = self._summaries[installation_id]
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        return s

    def get(self, installation_id: str) -> PlatformSummary:
        return self._summaries.get(installation_id, PlatformSummary())

    def health_grade(self, installation_id: str) -> str:
        s = self.get(installation_id)
        score = 0
        if s.api_error_rate < 1: score += 25
        elif s.api_error_rate < 5: score += 15
        if s.webhook_success_rate >= 99: score += 25
        elif s.webhook_success_rate >= 95: score += 15
        if s.open_incidents == 0: score += 25
        elif s.open_incidents <= 2: score += 10
        if s.documentation_coverage_pct >= 90: score += 25
        elif s.documentation_coverage_pct >= 70: score += 15
        if score >= 90: return "A"
        if score >= 75: return "B"
        if score >= 50: return "C"
        return "D"
