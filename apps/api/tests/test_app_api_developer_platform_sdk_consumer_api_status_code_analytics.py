import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_endpoint_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_status_code_analytics import (
    AppAPIDeveloperPlatformSDKConsumerApiStatusCodeAnalytics,
)

class TestStatusCodeAnalytics:
    def test_basic_analytics(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiStatusCodeAnalytics()
        for _ in range(80):
            svc.record("inst-1", "c1", 200)
        for _ in range(10):
            svc.record("inst-1", "c1", 400)
        for _ in range(10):
            svc.record("inst-1", "c1", 500)
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.success_rate_pct == 80.0 and analytics.server_error_rate_pct == 10.0

    def test_category_breakdown(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiStatusCodeAnalytics()
        svc.record("inst-1", "c1", 200)
        svc.record("inst-1", "c1", 201)
        svc.record("inst-1", "c1", 301)
        svc.record("inst-1", "c1", 404)
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.by_category["2xx"] == 2 and analytics.by_category["3xx"] == 1

    def test_top_codes(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiStatusCodeAnalytics()
        for _ in range(50):
            svc.record("inst-1", "c1", 200)
        for _ in range(30):
            svc.record("inst-1", "c1", 404)
        for _ in range(20):
            svc.record("inst-1", "c1", 500)
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.top_codes[0].status_code == 200

    def test_invalid_code(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiStatusCodeAnalytics()
        with pytest.raises(ValueError, match="Invalid"):
            svc.record("inst-1", "c1", 999)

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiStatusCodeAnalytics()
        assert svc.analyze("inst-1", "c1").total_requests == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiStatusCodeAnalytics()
        svc.record("inst-1", "c1", 200)
        assert svc.analyze("inst-2", "c1").total_requests == 0
