import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_consumer_api_consumer_api_consumer_endpoint_usage_analytics_v2 import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2, EndpointUsageRecord,
)

class TestEndpointUsageAnalyticsV2:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_basic_analytics(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2()
        for i in range(10):
            svc.record("inst-1", EndpointUsageRecord(endpoint_path="/api/users", method="GET", status_code=200, latency_ms=50 + i * 5, consumer_id="c1", timestamp=self._now() + timedelta(seconds=i)))
        analytics = svc.analyze("inst-1", "/api/users")
        assert analytics.total_requests == 10 and analytics.unique_consumers == 1

    def test_p95(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2()
        for i in range(100):
            svc.record("inst-1", EndpointUsageRecord(endpoint_path="/api", method="GET", status_code=200, latency_ms=float(i + 1), consumer_id="c1", timestamp=self._now()))
        analytics = svc.analyze("inst-1", "/api")
        assert analytics.p95_latency_ms == 96.0

    def test_error_rate(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2()
        svc.record("inst-1", EndpointUsageRecord(endpoint_path="/api", method="GET", status_code=200, latency_ms=50, consumer_id="c1", timestamp=self._now()))
        svc.record("inst-1", EndpointUsageRecord(endpoint_path="/api", method="GET", status_code=500, latency_ms=100, consumer_id="c1", timestamp=self._now()))
        assert svc.analyze("inst-1", "/api").error_rate_pct == 50.0

    def test_top_consumers(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2()
        for _ in range(5):
            svc.record("inst-1", EndpointUsageRecord(endpoint_path="/api", method="GET", status_code=200, latency_ms=50, consumer_id="c1", timestamp=self._now()))
        for _ in range(2):
            svc.record("inst-1", EndpointUsageRecord(endpoint_path="/api", method="GET", status_code=200, latency_ms=50, consumer_id="c2", timestamp=self._now()))
        analytics = svc.analyze("inst-1", "/api")
        assert analytics.top_consumers[0][0] == "c1" and analytics.unique_consumers == 2

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2()
        assert svc.analyze("inst-1", "/missing").total_requests == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2()
        svc.record("inst-1", EndpointUsageRecord(endpoint_path="/api", method="GET", status_code=200, latency_ms=50, consumer_id="c1", timestamp=self._now()))
        assert svc.analyze("inst-2", "/api").total_requests == 0
