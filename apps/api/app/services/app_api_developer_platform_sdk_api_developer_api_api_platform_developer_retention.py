"""App API Developer Platform Developer Retention — track developer retention cohorts."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RetentionCohort:
    cohort_month: str
    initial_count: int
    month_1: int = 0
    month_3: int = 0
    month_6: int = 0
    month_12: int = 0

    @property
    def retention_1m(self) -> float:
        return round(self.month_1 / self.initial_count * 100, 1) if self.initial_count > 0 else 0.0

    @property
    def retention_3m(self) -> float:
        return round(self.month_3 / self.initial_count * 100, 1) if self.initial_count > 0 else 0.0

    @property
    def retention_12m(self) -> float:
        return round(self.month_12 / self.initial_count * 100, 1) if self.initial_count > 0 else 0.0

    @property
    def health(self) -> str:
        r = self.retention_3m
        if r >= 70: return "excellent"
        if r >= 50: return "good"
        if r >= 30: return "fair"
        return "poor"

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetention:
    def __init__(self) -> None:
        self._cohorts: dict[tuple[str, str], RetentionCohort] = {}

    def record(self, installation_id: str, cohort_month: str, initial_count: int, **kwargs) -> RetentionCohort:
        if not installation_id: raise ValueError("installation_id is required")
        if initial_count < 1: raise ValueError("initial_count must be >= 1")
        key = (installation_id, cohort_month)
        c = RetentionCohort(cohort_month=cohort_month, initial_count=initial_count)
        for k, v in kwargs.items():
            if hasattr(c, k): setattr(c, k, v)
        self._cohorts[key] = c
        return c

    def avg_retention_3m(self, installation_id: str) -> float:
        cohorts = [c for (inst, _), c in self._cohorts.items() if inst == installation_id and c.month_3 > 0]
        if not cohorts: return 0.0
        return round(sum(c.retention_3m for c in cohorts) / len(cohorts), 1)

    def all_cohorts(self, installation_id: str) -> list[RetentionCohort]:
        return sorted([c for (inst, _), c in self._cohorts.items() if inst == installation_id], key=lambda c: c.cohort_month)
