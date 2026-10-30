import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_analytics import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalytics, AnalyticsDataPoint,
)

class TestConsumerApiAnalytics:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_summarize(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalytics()
        for i in range(5):
            svc.record("inst-1", "c1", AnalyticsDataPoint(timestamp=self._now() + timedelta(hours=i), metric="latency_ms", value=100 + i * 10))
        summary = svc.summarize("inst-1", "c1", "latency_ms")
        assert summary.data_points == 5 and summary.min_value == 100 and summary.max_value == 140

    def test_trend_up(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalytics()
        for i in range(10):
            svc.record("inst-1", "c1", AnalyticsDataPoint(timestamp=self._now() + timedelta(hours=i), metric="requests", value=100 + i * 50))
        summary = svc.summarize("inst-1", "c1", "requests")
        assert summary.trend == "up"

    def test_top_dimensions(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalytics()
        svc.record("inst-1", "c1", AnalyticsDataPoint(timestamp=self._now(), metric="requests", value=100, dimensions={"endpoint": "/api/users"}))
        svc.record("inst-1", "c1", AnalyticsDataPoint(timestamp=self._now(), metric="requests", value=50, dimensions={"endpoint": "/api/orders"}))
        top = svc.top_dimensions("inst-1", "c1", "requests", "endpoint")
        assert top[0][0] == "/api/users" and top[0][1] == 100

    def test_empty_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalytics()
        summary = svc.summarize("inst-1", "c1", "missing")
        assert summary.data_points == 0 and summary.trend == "flat"

    def test_get_metrics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalytics()
        svc.record("inst-1", "c1", AnalyticsDataPoint(timestamp=self._now(), metric="latency", value=1))
        svc.record("inst-1", "c1", AnalyticsDataPoint(timestamp=self._now(), metric="errors", value=2))
        assert svc.get_metrics("inst-1", "c1") == ["errors", "latency"]

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalytics()
        svc.record("inst-1", "c1", AnalyticsDataPoint(timestamp=self._now(), metric="x", value=1))
        assert len(svc.get_metrics("inst-2", "c1")) == 0
