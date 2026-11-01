"""Consumer API Error Budget Policy — define and enforce error budget policies."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ErrorBudgetPolicy:
    policy_id: str
    consumer_id: str
    slo_target_pct: float  # e.g. 99.9
    window_days: int = 30
    burn_rate_threshold: float = 1.0  # alert when burn rate exceeds this
    auto_throttle: bool = False  # auto-reduce rate limits when budget exhausted

@dataclass
class BudgetState:
    consumer_id: str
    total_requests: int
    error_count: int
    error_rate_pct: float
    budget_total: float
    budget_consumed: float
    budget_remaining_pct: float
    burn_rate: float  # errors per hour normalized
    alert: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], ErrorBudgetPolicy] = {}
        self._state: dict[tuple[str, str], dict] = {}

    def set_policy(self, installation_id: str, policy: ErrorBudgetPolicy) -> ErrorBudgetPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (90 <= policy.slo_target_pct <= 100):
            raise ValueError("slo_target_pct must be between 90 and 100")
        if policy.window_days < 1:
            raise ValueError("window_days must be positive")
        self._policies[(installation_id, policy.consumer_id)] = policy
        return policy

    def record(self, installation_id: str, consumer_id: str, total_requests: int, error_count: int, hours_elapsed: float = 1.0) -> BudgetState:
        key = (installation_id, consumer_id)
        policy = self._policies.get(key)
        if not policy:
            raise ValueError("No policy configured")
        if total_requests < 0 or error_count < 0:
            raise ValueError("Counts must be non-negative")
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
        error_budget = (100 - policy.slo_target_pct) / 100 * total_requests
        budget_consumed = error_count / error_budget * 100 if error_budget > 0 else 100
        remaining = max(0, 100 - budget_consumed)
        burn_rate = (error_count / hours_elapsed) if hours_elapsed > 0 else 0
        alert = burn_rate > policy.burn_rate_threshold or remaining <= 0
        state = BudgetState(
            consumer_id=consumer_id, total_requests=total_requests, error_count=error_count,
            error_rate_pct=round(error_rate, 3), budget_total=round(error_budget, 1),
            budget_consumed=round(budget_consumed, 1), budget_remaining_pct=round(remaining, 1),
            burn_rate=round(burn_rate, 2), alert=alert,
        )
        self._state[key] = {"state": state}
        return state

    def get_state(self, installation_id: str, consumer_id: str) -> BudgetState | None:
        s = self._state.get((installation_id, consumer_id))
        return s["state"] if s else None

    def get_policy(self, installation_id: str, consumer_id: str) -> ErrorBudgetPolicy | None:
        return self._policies.get((installation_id, consumer_id))
