"""Span Aggregator — aggregate trace spans into service-level metrics.

Turn raw spans into actionable insights: per-service latency,
error rates, throughput, and dependency maps.

Implements:
- Per-service latency percentiles (p50, p95, p99)
- Per-service error rate
- Service dependency map (who calls whom)
- Slowest endpoints ranking
- Throughput (requests/second per service)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import statistics
from collections import defaultdict


@dataclass
class Span:
    trace_id: str
    span_id: str
    service: str
    operation: str
    duration_ms: float
    status: str = "ok"  # ok, error
    parent_service: str = ""


class SpanAggregatorService:
    def __init__(self):
        self._spans: list[Span] = []

    def ingest(self, span: Span) -> None:
        self._spans.append(span)

    def ingest_batch(self, spans: list[Span]) -> int:
        self._spans.extend(spans)
        return len(spans)

    def service_latency(self, service: str) -> dict:
        """Per-service latency percentiles."""
        durations = [s.duration_ms for s in self._spans if s.service == service]
        if not durations:
            return {"count": 0}
        sorted_d = sorted(durations)
        n = len(sorted_d)
        return {
            "count": n,
            "mean": round(statistics.mean(durations), 2),
            "p50": sorted_d[n // 2],
            "p95": sorted_d[int(n * 0.95)],
            "p99": sorted_d[int(n * 0.99)],
            "min": sorted_d[0],
            "max": sorted_d[-1],
        }

    def service_error_rate(self, service: str) -> dict:
        spans = [s for s in self._spans if s.service == service]
        if not spans:
            return {"total": 0, "errors": 0, "rate": 0}
        errors = sum(1 for s in spans if s.status == "error")
        return {"total": len(spans), "errors": errors,
                "rate": round(errors / len(spans) * 100, 2)}

    def dependency_map(self) -> dict[str, set[str]]:
        """Who calls whom: {caller_service: {callee_services}}."""
        deps: dict[str, set[str]] = defaultdict(set)
        for span in self._spans:
            if span.parent_service and span.parent_service != span.service:
                deps[span.parent_service].add(span.service)
        return {k: sorted(v) for k, v in deps.items()}

    def slowest_operations(self, limit: int = 10) -> list[dict]:
        """Top N slowest operations across all services."""
        by_op: dict[str, list[float]] = defaultdict(list)
        for span in self._spans:
            key = f"{span.service}/{span.operation}"
            by_op[key].append(span.duration_ms)
        ranked = []
        for key, durations in by_op.items():
            ranked.append({
                "operation": key,
                "avg_ms": round(statistics.mean(durations), 2),
                "p99_ms": sorted(durations)[int(len(durations) * 0.99)],
                "count": len(durations),
            })
        ranked.sort(key=lambda x: -x["p99_ms"])
        return ranked[:limit]

    def throughput(self) -> dict[str, int]:
        """Request count per service."""
        counts: dict[str, int] = defaultdict(int)
        for span in self._spans:
            counts[span.service] += 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    def services(self) -> list[str]:
        return sorted(set(s.service for s in self._spans))

    def service_summary(self) -> list[dict]:
        """Summary for all services."""
        return [{"service": svc,
                 **self.service_latency(svc),
                 "error_rate": self.service_error_rate(svc)["rate"]}
                for svc in self.services()]
