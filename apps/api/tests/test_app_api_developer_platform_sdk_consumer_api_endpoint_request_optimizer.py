import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_endpoint_request_optimizer import (
    AppAPIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizer,
)

class TestEndpointRequestOptimizer:
    def test_low_cache_hit(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizer()
        report = svc.analyze("inst-1", "c1", avg_request_size_bytes=500, avg_response_size_bytes=2000, cache_hit_rate_pct=20, requests_per_minute=50, unique_endpoints=10)
        assert any(s.category == "caching" for s in report.suggestions)

    def test_large_response(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizer()
        report = svc.analyze("inst-1", "c1", avg_request_size_bytes=200, avg_response_size_bytes=50000, cache_hit_rate_pct=80, requests_per_minute=30, unique_endpoints=10)
        assert any(s.category == "compression" for s in report.suggestions)

    def test_batch_suggestion(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizer()
        report = svc.analyze("inst-1", "c1", avg_request_size_bytes=100, avg_response_size_bytes=500, cache_hit_rate_pct=90, requests_per_minute=200, unique_endpoints=3)
        assert any(s.category == "batching" for s in report.suggestions)

    def test_no_suggestions(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizer()
        report = svc.analyze("inst-1", "c1", avg_request_size_bytes=200, avg_response_size_bytes=1000, cache_hit_rate_pct=90, requests_per_minute=30, unique_endpoints=10)
        assert report.total_suggestions == 0

    def test_savings_capped(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizer()
        report = svc.analyze("inst-1", "c1", avg_request_size_bytes=10000, avg_response_size_bytes=50000, cache_hit_rate_pct=10, requests_per_minute=200, unique_endpoints=2)
        assert report.estimated_savings_pct <= 60

    def test_get_suggestions(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointRequestOptimizer()
        svc.analyze("inst-1", "c1", avg_request_size_bytes=100, avg_response_size_bytes=50000, cache_hit_rate_pct=10, requests_per_minute=10, unique_endpoints=10)
        assert len(svc.get_suggestions("inst-1", "c1")) >= 2
        assert len(svc.get_suggestions("inst-2", "c1")) == 0
