"""Endpoint Performance Budget — performance budget tracking with alerting."""
from __future__ import annotations

import statistics
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class PerfBudget:
    endpoint_id: str
    max_latency_p95_ms: float
    max_latency_p99_ms: float
    max_payload_bytes: int = 0
    max_error_rate_pct: float = 5.0


@dataclass
class PerfSample:
    endpoint_id: str
    latency_ms: float
    payload_bytes: int = 0
    is_error: bool = False


@dataclass
class PerfBudgetTracker:
    """Track endpoint performance against defined budgets."""

    _budgets: dict[str, PerfBudget] = field(default_factory=dict)
    _samples: dict[str, list[PerfSample]] = field(default_factory=dict)

    def set_budget(self, budget: PerfBudget) -> dict:
        if budget.max_latency_p95_ms <= 0:
            raise ValueError("max_latency_p95_ms must be positive")
        self._budgets[budget.endpoint_id] = budget
        logger.info("perf_budget_set", endpoint_id=budget.endpoint_id)
        return {"endpoint_id": budget.endpoint_id, "configured": True}

    def record(self, sample: PerfSample) -> dict:
        self._samples.setdefault(sample.endpoint_id, []).append(sample)
        return {"endpoint_id": sample.endpoint_id,
                "total_samples": len(self._samples[sample.endpoint_id])}

    def check_budget(self, endpoint_id: str) -> dict:
        budget = self._budgets.get(endpoint_id)
        if not budget:
            return {"endpoint_id": endpoint_id, "status": "no_budget"}
        samples = self._samples.get(endpoint_id, [])
        if len(samples) < 2:
            return {"endpoint_id": endpoint_id, "status": "insufficient_data"}
        latencies = sorted(s.latency_ms for s in samples)
        n = len(latencies)
        p95 = latencies[int(n * 0.95)] if n > 1 else latencies[0]
        p99 = latencies[min(int(n * 0.99), n - 1)]
        errors = sum(1 for s in samples if s.is_error)
        error_rate = errors / n * 100
        violations = []
        if p95 > budget.max_latency_p95_ms:
            violations.append({"metric": "latency_p95", "actual": round(p95, 2),
                               "budget": budget.max_latency_p95_ms})
        if p99 > budget.max_latency_p99_ms:
            violations.append({"metric": "latency_p99", "actual": round(p99, 2),
                               "budget": budget.max_latency_p99_ms})
        if error_rate > budget.max_error_rate_pct:
            violations.append({"metric": "error_rate", "actual": round(error_rate, 2),
                               "budget": budget.max_error_rate_pct})
        if budget.max_payload_bytes > 0:
            max_payload = max(s.payload_bytes for s in samples)
            if max_payload > budget.max_payload_bytes:
                violations.append({"metric": "payload_size", "actual": max_payload,
                                   "budget": budget.max_payload_bytes})
        status = "within_budget" if not violations else "over_budget"
        return {
            "endpoint_id": endpoint_id,
            "status": status,
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
            "error_rate_pct": round(error_rate, 2),
            "sample_count": n,
            "violations": violations,
        }

    def get_all_budgets(self) -> list[dict]:
        results = []
        for eid in self._budgets:
            results.append(self.check_budget(eid))
        return results

    def get_stats(self) -> dict:
        total = len(self._budgets)
        checks = [self.check_budget(eid) for eid in self._budgets]
        within = sum(1 for c in checks if c.get("status") == "within_budget")
        over = sum(1 for c in checks if c.get("status") == "over_budget")
        return {"total_budgets": total, "within_budget": within,
                "over_budget": over, "unchecked": total - within - over}
