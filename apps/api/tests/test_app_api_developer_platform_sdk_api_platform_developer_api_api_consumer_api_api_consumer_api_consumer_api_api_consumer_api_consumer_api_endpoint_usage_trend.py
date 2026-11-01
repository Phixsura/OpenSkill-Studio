import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_endpoint_usage_trend import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrend, UsagePeriod,
)

class TestEndpointUsageTrend:
    def test_growing(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrend()
        for i, period in enumerate(["2026-01", "2026-02", "2026-03", "2026-04"]):
            svc.record_period("inst-1", "/api", UsagePeriod(period=period, request_count=1000 + i * 500, error_count=0, avg_latency_ms=50))
        trend = svc.get_trend("inst-1", "/api")
        assert trend.trend_direction == "growing" and trend.growth_rate_pct > 0

    def test_stable(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrend()
        for period in ["2026-01", "2026-02", "2026-03"]:
            svc.record_period("inst-1", "/api", UsagePeriod(period=period, request_count=1000, error_count=0, avg_latency_ms=50))
        trend = svc.get_trend("inst-1", "/api")
        assert trend.trend_direction == "stable"

    def test_declining(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrend()
        for i, period in enumerate(["2026-01", "2026-02", "2026-03", "2026-04"]):
            svc.record_period("inst-1", "/api", UsagePeriod(period=period, request_count=2000 - i * 500, error_count=0, avg_latency_ms=50))
        trend = svc.get_trend("inst-1", "/api")
        assert trend.trend_direction == "declining"

    def test_single_period(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrend()
        svc.record_period("inst-1", "/api", UsagePeriod(period="2026-01", request_count=500, error_count=0, avg_latency_ms=50))
        trend = svc.get_trend("inst-1", "/api")
        assert trend.trend_direction == "stable" and len(trend.periods) == 1

    def test_list_endpoints(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrend()
        svc.record_period("inst-1", "/api/users", UsagePeriod(period="2026-01", request_count=100, error_count=0, avg_latency_ms=50))
        svc.record_period("inst-1", "/api/orders", UsagePeriod(period="2026-01", request_count=200, error_count=0, avg_latency_ms=50))
        endpoints = svc.list_endpoints("inst-1")
        assert endpoints == ["/api/orders", "/api/users"]

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrend()
        svc.record_period("inst-1", "/api", UsagePeriod(period="2026-01", request_count=100, error_count=0, avg_latency_ms=50))
        assert len(svc.list_endpoints("inst-2")) == 0
