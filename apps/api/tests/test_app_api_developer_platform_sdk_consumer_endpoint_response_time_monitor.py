import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_endpoint_response_time_monitor import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerApiEndpointResponseTimeMonitor, ResponseTimeTarget, ResponseTimeSample,
)

class TestEndpointResponseTimeMonitor:
    def test_within_targets(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerApiEndpointResponseTimeMonitor()
        svc.set_target("inst-1", ResponseTimeTarget(endpoint_path="/api", p50_target_ms=100, p95_target_ms=500, p99_target_ms=1000))
        for i in range(100):
            svc.record_sample("inst-1", ResponseTimeSample(endpoint_path="/api", latency_ms=50 + i * 0.5))
        report = svc.get_report("inst-1", "/api")
        assert report.all_ok and report.sample_count == 100

    def test_p99_breach(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerApiEndpointResponseTimeMonitor()
        svc.set_target("inst-1", ResponseTimeTarget(endpoint_path="/api", p99_target_ms=100))
        for i in range(100):
            svc.record_sample("inst-1", ResponseTimeSample(endpoint_path="/api", latency_ms=50 + i * 3))
        report = svc.get_report("inst-1", "/api")
        assert not report.p99_ok

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerApiEndpointResponseTimeMonitor()
        report = svc.get_report("inst-1", "/api")
        assert report.sample_count == 0 and report.all_ok

    def test_invalid_targets(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerApiEndpointResponseTimeMonitor()
        with pytest.raises(ValueError, match="ascending"):
            svc.set_target("inst-1", ResponseTimeTarget(endpoint_path="/api", p50_target_ms=500, p95_target_ms=100))

    def test_list_endpoints(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerApiEndpointResponseTimeMonitor()
        svc.set_target("inst-1", ResponseTimeTarget(endpoint_path="/api/users"))
        svc.set_target("inst-1", ResponseTimeTarget(endpoint_path="/api/orders"))
        assert svc.list_endpoints("inst-1") == ["/api/orders", "/api/users"]

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerApiEndpointResponseTimeMonitor()
        svc.set_target("inst-1", ResponseTimeTarget(endpoint_path="/api"))
        assert len(svc.list_endpoints("inst-2")) == 0
