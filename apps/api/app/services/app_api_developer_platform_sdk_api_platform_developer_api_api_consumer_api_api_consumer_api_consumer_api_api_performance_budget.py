"""Consumer API Performance Budget — track and enforce performance budgets."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PerformanceBudget:
    budget_id: str
    endpoint_path: str
    max_p50_ms: float = 100
    max_p95_ms: float = 500
    max_p99_ms: float = 1000
    max_error_rate_pct: float = 1.0

@dataclass
class PerformanceSnapshot:
    endpoint_path: str
    p50_ms: float
    p95_ms: float
    p99_ms: float
    error_rate_pct: float
    request_count: int

@dataclass
class BudgetViolation:
    endpoint_path: str
    metric: str
    budget_value: float
    actual_value: float

@dataclass
class BudgetReport:
    endpoint_path: str
    within_budget: bool
    violations: list[BudgetViolation] = field(default_factory=list)
    score: float = 100.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], PerformanceBudget] = {}

    def set_budget(self, installation_id: str, budget: PerformanceBudget) -> PerformanceBudget:
        if not installation_id:
            raise ValueError("installation_id is required")
        if budget.max_p50_ms > budget.max_p95_ms or budget.max_p95_ms > budget.max_p99_ms:
            raise ValueError("Percentile budgets must be in ascending order")
        self._budgets[(installation_id, budget.endpoint_path)] = budget
        return budget

    def evaluate(self, installation_id: str, snapshot: PerformanceSnapshot) -> BudgetReport:
        budget = self._budgets.get((installation_id, snapshot.endpoint_path))
        if not budget:
            return BudgetReport(endpoint_path=snapshot.endpoint_path, within_budget=True, score=100.0)
        violations: list[BudgetViolation] = []
        if snapshot.p50_ms > budget.max_p50_ms:
            violations.append(BudgetViolation(endpoint_path=snapshot.endpoint_path, metric="p50", budget_value=budget.max_p50_ms, actual_value=snapshot.p50_ms))
        if snapshot.p95_ms > budget.max_p95_ms:
            violations.append(BudgetViolation(endpoint_path=snapshot.endpoint_path, metric="p95", budget_value=budget.max_p95_ms, actual_value=snapshot.p95_ms))
        if snapshot.p99_ms > budget.max_p99_ms:
            violations.append(BudgetViolation(endpoint_path=snapshot.endpoint_path, metric="p99", budget_value=budget.max_p99_ms, actual_value=snapshot.p99_ms))
        if snapshot.error_rate_pct > budget.max_error_rate_pct:
            violations.append(BudgetViolation(endpoint_path=snapshot.endpoint_path, metric="error_rate", budget_value=budget.max_error_rate_pct, actual_value=snapshot.error_rate_pct))
        # Score: 100 minus 25 per violation
        score = max(0, 100 - len(violations) * 25)
        return BudgetReport(endpoint_path=snapshot.endpoint_path, within_budget=len(violations) == 0, violations=violations, score=float(score))

    def list_budgets(self, installation_id: str) -> list[PerformanceBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]
