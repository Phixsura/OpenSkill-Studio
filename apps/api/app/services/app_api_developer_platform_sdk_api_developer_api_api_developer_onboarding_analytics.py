"""App API Developer Onboarding Analytics — analyze developer onboarding effectiveness."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class OnboardingAnalytics:
    total_started: int = 0
    total_completed: int = 0
    avg_time_to_first_call_hours: float = 0.0
    avg_completion_time_hours: float = 0.0
    drop_off_step: str = ""
    drop_off_rate_pct: float = 0.0

    @property
    def completion_rate(self) -> float:
        return round(self.total_completed / self.total_started * 100, 1) if self.total_started > 0 else 0.0

    @property
    def quality(self) -> str:
        r = self.completion_rate
        if r >= 80: return "excellent"
        if r >= 60: return "good"
        if r >= 40: return "needs_improvement"
        return "poor"

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[str, OnboardingAnalytics] = {}

    def update(self, installation_id: str, **kwargs) -> OnboardingAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        a = OnboardingAnalytics()
        for k, v in kwargs.items():
            if hasattr(a, k): setattr(a, k, v)
        self._analytics[installation_id] = a
        return a

    def get(self, installation_id: str) -> OnboardingAnalytics:
        return self._analytics.get(installation_id, OnboardingAnalytics())
