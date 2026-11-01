import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_usage_insight import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsight,
)

class TestConsumerApiUsageInsight:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_high_error_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsight()
        insights = svc.generate("inst-1", "c1", error_rate=8.0, avg_latency_ms=100, daily_requests=1000, unused_endpoints=0, now=self._now())
        assert any(i.severity == "critical" and "Error Rate" in i.title for i in insights)

    def test_high_latency(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsight()
        insights = svc.generate("inst-1", "c1", error_rate=0.1, avg_latency_ms=800, daily_requests=1000, unused_endpoints=0, now=self._now())
        assert any("Latency" in i.title for i in insights)

    def test_high_volume(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsight()
        insights = svc.generate("inst-1", "c1", error_rate=0.1, avg_latency_ms=50, daily_requests=100000, unused_endpoints=0, now=self._now())
        assert any("Volume" in i.title for i in insights)

    def test_no_issues(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsight()
        insights = svc.generate("inst-1", "c1", error_rate=0.1, avg_latency_ms=50, daily_requests=1000, unused_endpoints=0, now=self._now())
        assert len(insights) == 0

    def test_filter_by_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsight()
        svc.generate("inst-1", "c1", error_rate=8.0, avg_latency_ms=800, daily_requests=100000, unused_endpoints=10, now=self._now())
        perf = svc.get_insights("inst-1", "c1", category="performance")
        assert all(i.category == "performance" for i in perf)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiUsageInsight()
        svc.generate("inst-1", "c1", error_rate=8.0, avg_latency_ms=100, daily_requests=100, unused_endpoints=0, now=self._now())
        assert len(svc.get_insights("inst-2", "c1")) == 0
