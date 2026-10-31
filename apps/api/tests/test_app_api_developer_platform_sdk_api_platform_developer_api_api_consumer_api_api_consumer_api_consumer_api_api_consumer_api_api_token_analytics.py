import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_token_analytics import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalytics, TokenUsageRecord,
)

class TestConsumerApiTokenAnalytics:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_record_and_analytics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalytics()
        svc.record("inst-1", TokenUsageRecord(token_id="t1", consumer_id="c1", endpoint="/api/users", method="GET", status_code=200, timestamp=self._now(), ip_address="1.2.3.4"))
        analytics = svc.get_analytics("inst-1", "c1", "t1")
        assert analytics.total_requests == 1 and analytics.unique_ips == 1

    def test_top_endpoints(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalytics()
        for _ in range(5):
            svc.record("inst-1", TokenUsageRecord(token_id="t1", consumer_id="c1", endpoint="/api/users", method="GET", status_code=200, timestamp=self._now()))
        for _ in range(3):
            svc.record("inst-1", TokenUsageRecord(token_id="t1", consumer_id="c1", endpoint="/api/orders", method="POST", status_code=201, timestamp=self._now()))
        analytics = svc.get_analytics("inst-1", "c1", "t1")
        assert analytics.top_endpoints[0][0] == "GET /api/users"

    def test_error_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalytics()
        svc.record("inst-1", TokenUsageRecord(token_id="t1", consumer_id="c1", endpoint="/api", method="GET", status_code=200, timestamp=self._now()))
        svc.record("inst-1", TokenUsageRecord(token_id="t1", consumer_id="c1", endpoint="/api", method="GET", status_code=500, timestamp=self._now()))
        assert svc.get_analytics("inst-1", "c1", "t1").error_count == 1

    def test_anomaly_new_ip(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalytics()
        svc.record("inst-1", TokenUsageRecord(token_id="t1", consumer_id="c1", endpoint="/api", method="GET", status_code=200, timestamp=self._now() - timedelta(hours=2), ip_address="1.1.1.1"))
        svc.record("inst-1", TokenUsageRecord(token_id="t1", consumer_id="c1", endpoint="/api", method="GET", status_code=200, timestamp=self._now(), ip_address="9.9.9.9"))
        anomaly = svc.detect_anomaly("inst-1", "c1", "t1", window_hours=1, now=self._now())
        assert anomaly["new_ips_detected"]

    def test_empty_analytics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalytics()
        analytics = svc.get_analytics("inst-1", "c1", "missing")
        assert analytics.total_requests == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalytics()
        svc.record("inst-1", TokenUsageRecord(token_id="t1", consumer_id="c1", endpoint="/api", method="GET", status_code=200, timestamp=self._now()))
        assert svc.get_analytics("inst-2", "c1", "t1").total_requests == 0
