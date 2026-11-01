"""Platform Metrics Aggregator — final aggregation of all platform metrics.

The capstone service: aggregates all 263+ backend services into a unified
platform health, performance, and growth report.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PlatformMetrics:
    total_services: int = 0
    backend_services: int = 0
    frontend_components: int = 0
    total_tests: int = 0
    total_commits: int = 0
    test_pass_rate: float = 100.0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    uptime_percent: float = 99.99
    developer_count: int = 0
    extension_count: int = 0
    install_count: int = 0


class PlatformMetricsAggService:
    """Final aggregation of all platform metrics."""

    def __init__(self):
        self._metrics = PlatformMetrics()

    def update(self, **kwargs) -> PlatformMetrics:
        for k, v in kwargs.items():
            if hasattr(self._metrics, k):
                setattr(self._metrics, k, v)
        return self._metrics

    def get_report(self) -> dict:
        m = self._metrics
        return {
            "platform": {
                "services": m.total_services,
                "backend": m.backend_services,
                "frontend": m.frontend_components,
                "tests": m.total_tests,
                "commits": m.total_commits,
            },
            "quality": {
                "test_pass_rate": m.test_pass_rate,
                "avg_latency_ms": m.avg_latency_ms,
                "error_rate": m.error_rate,
                "uptime": m.uptime_percent,
            },
            "growth": {
                "developers": m.developer_count,
                "extensions": m.extension_count,
                "installs": m.install_count,
            },
            "dora": self._calc_dora(m),
        }

    def _calc_dora(self, m: PlatformMetrics) -> dict:
        # DORA metrics approximation
        deploy_freq = "multiple_per_day" if m.total_commits > 4000 else "daily"
        lead_time = "less_than_hour" if m.test_pass_rate >= 99 else "less_than_day"
        change_fail = "less_than_5pct" if m.error_rate < 5 else "5_to_15pct"
        mttr = "less_than_hour" if m.uptime_percent >= 99.9 else "less_than_day"
        return {
            "deployment_frequency": deploy_freq,
            "lead_time_for_changes": lead_time,
            "change_failure_rate": change_fail,
            "time_to_restore": mttr,
            "classification": "elite" if all([
                deploy_freq == "multiple_per_day",
                lead_time == "less_than_hour",
                change_fail == "less_than_5pct",
                mttr == "less_than_hour",
            ]) else "high",
        }
