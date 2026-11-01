"""App API Latency Budget — track and enforce latency SLOs.

Manages latency budgets:
- Define p50/p95/p99 targets per endpoint
- Record latency samples
- Calculate percentiles
- Alert on budget violations
- Per-installation scoped budgets
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class LatencyBudget:
    """A latency budget for an endpoint."""

    endpoint: str
    p50_target_ms: float
    p95_target_ms: float
    p99_target_ms: float
    samples: list[float] = field(default_factory=list)

    def percentile(self, pct: float) -> float:
        if not self.samples:
            return 0.0
        sorted_s = sorted(self.samples)
        idx = int(len(sorted_s) * pct / 100)
        return sorted_s[min(idx, len(sorted_s) - 1)]

    @property
    def p50(self) -> float:
        return self.percentile(50)

    @property
    def p95(self) -> float:
        return self.percentile(95)

    @property
    def p99(self) -> float:
        return self.percentile(99)

    @property
    def violations(self) -> list[str]:
        v = []
        if self.samples and self.p50 > self.p50_target_ms:
            v.append("p50")
        if self.samples and self.p95 > self.p95_target_ms:
            v.append("p95")
        if self.samples and self.p99 > self.p99_target_ms:
            v.append("p99")
        return v


class AppAPILatencyBudget:
    """Track and enforce latency SLOs."""

    def __init__(self, max_samples: int = 1000) -> None:
        self._max = max(1, max_samples)
        self._budgets: dict[tuple[str, str], LatencyBudget] = {}

    def set_budget(
        self, installation_id: str, endpoint: str,
        p50_ms: float, p95_ms: float, p99_ms: float,
    ) -> LatencyBudget:
        if not installation_id:
            raise ValueError("installation_id is required")
        budget = LatencyBudget(
            endpoint=endpoint, p50_target_ms=p50_ms,
            p95_target_ms=p95_ms, p99_target_ms=p99_ms,
        )
        self._budgets[(installation_id, endpoint)] = budget
        return budget

    def record(self, installation_id: str, endpoint: str, latency_ms: float) -> LatencyBudget:
        b = self._get(installation_id, endpoint)
        b.samples.append(latency_ms)
        if len(b.samples) > self._max:
            b.samples = b.samples[-self._max:]
        return b

    def check_violations(self, installation_id: str) -> list[dict]:
        results = []
        for (inst, _), b in self._budgets.items():
            if inst == installation_id and b.violations:
                results.append({"endpoint": b.endpoint, "violations": b.violations})
        return results

    def get_budget(self, installation_id: str, endpoint: str) -> LatencyBudget:
        return self._get(installation_id, endpoint)

    def list_budgets(self, installation_id: str) -> list[LatencyBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]

    def _get(self, installation_id: str, endpoint: str) -> LatencyBudget:
        key = (installation_id, endpoint)
        b = self._budgets.get(key)
        if b is None:
            raise KeyError(f"Budget for {endpoint} not found")
        return b
