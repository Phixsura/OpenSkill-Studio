import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_performance_budget import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudget, PerformanceBudget, PerformanceSnapshot,
)

class TestConsumerApiPerformanceBudget:
    def test_within_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudget()
        svc.set_budget("inst-1", PerformanceBudget(budget_id="b1", endpoint_path="/api", max_p50_ms=100, max_p95_ms=500, max_p99_ms=1000))
        report = svc.evaluate("inst-1", PerformanceSnapshot(endpoint_path="/api", p50_ms=50, p95_ms=200, p99_ms=800, error_rate_pct=0.1, request_count=1000))
        assert report.within_budget and report.score == 100

    def test_violations(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudget()
        svc.set_budget("inst-1", PerformanceBudget(budget_id="b1", endpoint_path="/api", max_p50_ms=50, max_p95_ms=200, max_p99_ms=500))
        report = svc.evaluate("inst-1", PerformanceSnapshot(endpoint_path="/api", p50_ms=100, p95_ms=300, p99_ms=400, error_rate_pct=0.5, request_count=500))
        assert not report.within_budget and len(report.violations) == 2  # p50 and p95

    def test_no_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudget()
        report = svc.evaluate("inst-1", PerformanceSnapshot(endpoint_path="/api", p50_ms=999, p95_ms=999, p99_ms=999, error_rate_pct=50, request_count=10))
        assert report.within_budget

    def test_invalid_percentile_order(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudget()
        with pytest.raises(ValueError, match="ascending"):
            svc.set_budget("inst-1", PerformanceBudget(budget_id="b1", endpoint_path="/api", max_p50_ms=500, max_p95_ms=100, max_p99_ms=1000))

    def test_score_calculation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudget()
        svc.set_budget("inst-1", PerformanceBudget(budget_id="b1", endpoint_path="/api", max_p50_ms=10, max_p95_ms=10, max_p99_ms=10, max_error_rate_pct=0.0))
        report = svc.evaluate("inst-1", PerformanceSnapshot(endpoint_path="/api", p50_ms=100, p95_ms=100, p99_ms=100, error_rate_pct=5, request_count=100))
        assert report.score == 0  # 4 violations * 25 = 100 deducted

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiPerformanceBudget()
        svc.set_budget("inst-1", PerformanceBudget(budget_id="b1", endpoint_path="/api"))
        assert len(svc.list_budgets("inst-2")) == 0
