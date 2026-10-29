"""App API Developer Error Budget Policy — define and enforce error budget policies."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ErrorBudgetPolicy:
    policy_id: str
    endpoint: str
    slo_pct: float
    window_days: int
    total_requests: int = 0
    failed_requests: int = 0
    freeze_on_exhaust: bool = True

    @property
    def allowed_failures(self) -> int:
        return int(self.total_requests * (100 - self.slo_pct) / 100)

    @property
    def remaining_failures(self) -> int:
        return max(0, self.allowed_failures - self.failed_requests)

    @property
    def exhausted(self) -> bool:
        return self.total_requests > 0 and self.remaining_failures == 0

    @property
    def burn_rate(self) -> float:
        if self.allowed_failures == 0: return 0.0
        return round(self.failed_requests / max(self.allowed_failures, 1), 2)

class AppAPIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], ErrorBudgetPolicy] = {}

    def create(self, installation_id: str, policy_id: str, endpoint: str, slo_pct: float, window_days: int, freeze_on_exhaust: bool = True) -> ErrorBudgetPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if not 90 <= slo_pct <= 100: raise ValueError("slo_pct must be 90-100")
        if window_days < 1: raise ValueError("window_days must be >= 1")
        key = (installation_id, policy_id)
        p = ErrorBudgetPolicy(policy_id=policy_id, endpoint=endpoint, slo_pct=slo_pct, window_days=window_days, freeze_on_exhaust=freeze_on_exhaust)
        self._policies[key] = p
        return p

    def record(self, installation_id: str, policy_id: str, success: bool) -> ErrorBudgetPolicy:
        key = (installation_id, policy_id)
        p = self._policies.get(key)
        if p is None: raise KeyError(f"Policy {policy_id} not found")
        p.total_requests += 1
        if not success: p.failed_requests += 1
        return p

    def should_freeze(self, installation_id: str, policy_id: str) -> bool:
        key = (installation_id, policy_id)
        p = self._policies.get(key)
        if p is None: return False
        return p.exhausted and p.freeze_on_exhaust

    def exhausted_policies(self, installation_id: str) -> list[ErrorBudgetPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id and p.exhausted]

    def all_policies(self, installation_id: str) -> list[ErrorBudgetPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]
