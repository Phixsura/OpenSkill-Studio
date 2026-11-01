import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_endpoint_metric_aggregator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregator,
)

class TestEndpointMetricAggregator:
    def test_record_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregator()
        svc.record("inst-1", "/api/users", 50)
        svc.record("inst-1", "/api/users", 100)
        m = svc.get_metric("inst-1", "/api/users")
        assert m.request_count == 2 and m.avg_latency_ms == 75.0

    def test_min_max(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregator()
        svc.record("inst-1", "/api", 10)
        svc.record("inst-1", "/api", 500)
        m = svc.get_metric("inst-1", "/api")
        assert m.min_latency_ms == 10 and m.max_latency_ms == 500

    def test_error_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregator()
        svc.record("inst-1", "/api", 50, is_error=False)
        svc.record("inst-1", "/api", 50, is_error=True)
        assert svc.get_metric("inst-1", "/api").error_rate_pct == 50.0

    def test_aggregate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregator()
        for _ in range(10):
            svc.record("inst-1", "/api/users", 50)
        for _ in range(5):
            svc.record("inst-1", "/api/orders", 200)
        agg = svc.aggregate("inst-1")
        assert agg.total_requests == 15 and agg.top_endpoints[0].endpoint_path == "/api/users"
        assert agg.slowest_endpoints[0].endpoint_path == "/api/orders"

    def test_empty_aggregate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregator()
        agg = svc.aggregate("inst-1")
        assert agg.total_requests == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregator()
        svc.record("inst-1", "/api", 50)
        assert svc.get_metric("inst-2", "/api") is None
