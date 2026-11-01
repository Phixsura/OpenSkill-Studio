import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_rate_limit_analytics import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalytics, RateLimitEvent,
)

class TestConsumerApiRateLimitAnalytics:
    def _now(self):
        return datetime(2026, 6, 1, 14, 0, 0)

    def test_basic_analytics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalytics()
        for i in range(10):
            svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api", allowed=True, timestamp=self._now()))
        svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api", allowed=False, timestamp=self._now(), remaining=0))
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.total_requests == 11 and analytics.throttled_count == 1

    def test_throttle_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalytics()
        for i in range(5):
            svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api", allowed=True, timestamp=self._now()))
        for i in range(5):
            svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api", allowed=False, timestamp=self._now()))
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.throttle_rate_pct == 50.0

    def test_most_throttled_endpoint(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalytics()
        svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api/a", allowed=False, timestamp=self._now()))
        svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api/b", allowed=False, timestamp=self._now()))
        svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api/b", allowed=False, timestamp=self._now()))
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.most_throttled_endpoint == "/api/b"

    def test_throttled_only_filter(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalytics()
        svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api", allowed=True, timestamp=self._now()))
        svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api", allowed=False, timestamp=self._now()))
        events = svc.get_events("inst-1", "c1", throttled_only=True)
        assert len(events) == 1 and not events[0].allowed

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalytics()
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.total_requests == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalytics()
        svc.record("inst-1", RateLimitEvent(consumer_id="c1", endpoint="/api", allowed=True, timestamp=self._now()))
        assert svc.analyze("inst-2", "c1").total_requests == 0
