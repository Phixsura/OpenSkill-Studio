import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_health_score import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScore, EndpointMetrics,
)

class TestEndpointHealthScore:
    def test_healthy_endpoint(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScore()
        svc.record_metrics("inst-1", EndpointMetrics(endpoint_path="/api", uptime_pct=99.99, avg_latency_ms=50, error_rate_pct=0.01, p99_latency_ms=150, request_count=10000))
        result = svc.compute("inst-1", "/api")
        assert result.grade == "A" and result.status == "healthy"

    def test_degraded_endpoint(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScore()
        svc.record_metrics("inst-1", EndpointMetrics(endpoint_path="/api", uptime_pct=97, avg_latency_ms=500, error_rate_pct=3, p99_latency_ms=1000, request_count=5000))
        result = svc.compute("inst-1", "/api")
        assert result.status == "degraded"

    def test_unhealthy_endpoint(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScore()
        svc.record_metrics("inst-1", EndpointMetrics(endpoint_path="/api", uptime_pct=90, avg_latency_ms=3000, error_rate_pct=15, p99_latency_ms=5000, request_count=100))
        result = svc.compute("inst-1", "/api")
        assert result.grade == "F" and result.status == "unhealthy"

    def test_compute_all(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScore()
        svc.record_metrics("inst-1", EndpointMetrics(endpoint_path="/a", uptime_pct=99.9, avg_latency_ms=50, error_rate_pct=0.1, p99_latency_ms=100, request_count=1000))
        svc.record_metrics("inst-1", EndpointMetrics(endpoint_path="/b", uptime_pct=95, avg_latency_ms=1000, error_rate_pct=5, p99_latency_ms=2000, request_count=500))
        scores = svc.compute_all("inst-1")
        assert len(scores) == 2 and scores[0].score >= scores[1].score

    def test_no_metrics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScore()
        with pytest.raises(ValueError, match="No metrics"):
            svc.compute("inst-1", "/missing")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScore()
        svc.record_metrics("inst-1", EndpointMetrics(endpoint_path="/api", uptime_pct=99, avg_latency_ms=100, error_rate_pct=1, p99_latency_ms=200, request_count=100))
        assert len(svc.compute_all("inst-2")) == 0
