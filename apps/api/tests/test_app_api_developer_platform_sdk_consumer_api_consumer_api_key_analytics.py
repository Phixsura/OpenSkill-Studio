import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_key_analytics import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalytics, KeyUsageRecord,
)

class TestConsumerApiKeyAnalytics:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_analytics(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalytics()
        svc.record("inst-1", "c1", KeyUsageRecord(key_id="k1", endpoint="/api/users", method="GET", status_code=200, latency_ms=50, timestamp=self._now()))
        analytics = svc.get_analytics("inst-1", "c1", "k1")
        assert analytics.total_requests == 1 and analytics.avg_latency_ms == 50

    def test_error_rate(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalytics()
        svc.record("inst-1", "c1", KeyUsageRecord(key_id="k1", endpoint="/api", method="GET", status_code=200, latency_ms=50, timestamp=self._now()))
        svc.record("inst-1", "c1", KeyUsageRecord(key_id="k1", endpoint="/api", method="GET", status_code=500, latency_ms=100, timestamp=self._now()))
        analytics = svc.get_analytics("inst-1", "c1", "k1")
        assert analytics.error_rate_pct == 50.0

    def test_top_endpoints(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalytics()
        for _ in range(5):
            svc.record("inst-1", "c1", KeyUsageRecord(key_id="k1", endpoint="/api/users", method="GET", status_code=200, latency_ms=50, timestamp=self._now()))
        for _ in range(2):
            svc.record("inst-1", "c1", KeyUsageRecord(key_id="k1", endpoint="/api/orders", method="POST", status_code=201, latency_ms=80, timestamp=self._now()))
        analytics = svc.get_analytics("inst-1", "c1", "k1")
        assert analytics.top_endpoints[0][0] == "GET /api/users"

    def test_compare_keys(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalytics()
        for _ in range(10):
            svc.record("inst-1", "c1", KeyUsageRecord(key_id="k1", endpoint="/api", method="GET", status_code=200, latency_ms=50, timestamp=self._now()))
        for _ in range(3):
            svc.record("inst-1", "c1", KeyUsageRecord(key_id="k2", endpoint="/api", method="GET", status_code=200, latency_ms=50, timestamp=self._now()))
        comparison = svc.compare_keys("inst-1", "c1")
        assert len(comparison) == 2 and comparison[0].key_id == "k1"

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalytics()
        analytics = svc.get_analytics("inst-1", "c1", "missing")
        assert analytics.total_requests == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalytics()
        svc.record("inst-1", "c1", KeyUsageRecord(key_id="k1", endpoint="/api", method="GET", status_code=200, latency_ms=50, timestamp=self._now()))
        assert svc.get_analytics("inst-2", "c1", "k1").total_requests == 0
