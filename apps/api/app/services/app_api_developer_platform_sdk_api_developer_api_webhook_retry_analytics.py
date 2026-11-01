"""App API Developer Webhook Retry Analytics — analyze retry patterns and effectiveness."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RetryAnalytics:
    destination: str
    total_retries: int = 0
    successful_retries: int = 0
    exhausted_retries: int = 0  # hit max retries
    avg_attempts_before_success: float = 0.0

    @property
    def retry_success_rate(self) -> float:
        return round(self.successful_retries / self.total_retries * 100, 1) if self.total_retries > 0 else 0.0

    @property
    def waste_rate(self) -> float:
        return round(self.exhausted_retries / self.total_retries * 100, 1) if self.total_retries > 0 else 0.0

class AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[tuple[str, str], RetryAnalytics] = {}

    def record(self, installation_id: str, destination: str, retries: int, success: bool, exhausted: bool = False) -> RetryAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, destination)
        if key not in self._analytics:
            self._analytics[key] = RetryAnalytics(destination=destination)
        a = self._analytics[key]
        a.total_retries += retries
        if success: a.successful_retries += retries
        if exhausted: a.exhausted_retries += 1
        return a

    def high_waste(self, installation_id: str, threshold_pct: float = 20) -> list[RetryAnalytics]:
        return [a for (inst, _), a in self._analytics.items() if inst == installation_id and a.waste_rate >= threshold_pct]

    def all_analytics(self, installation_id: str) -> list[RetryAnalytics]:
        return [a for (inst, _), a in self._analytics.items() if inst == installation_id]

    def total_retries(self, installation_id: str) -> int:
        return sum(a.total_retries for (inst, _), a in self._analytics.items() if inst == installation_id)
