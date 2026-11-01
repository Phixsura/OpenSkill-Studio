import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_endpoint_error_distribution import (
    AppAPIDeveloperPlatformSDKConsumerApiEndpointErrorDistribution,
)

class TestEndpointErrorDistribution:
    def test_basic_distribution(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointErrorDistribution()
        for _ in range(100):
            svc.record_request("inst-1", "/api")
        for _ in range(5):
            svc.record_error("inst-1", "/api", 400, "BAD_REQUEST")
        for _ in range(3):
            svc.record_error("inst-1", "/api", 500, "INTERNAL")
        dist = svc.get_distribution("inst-1", "/api")
        assert dist.total_errors == 8 and dist.most_common_error == "BAD_REQUEST"

    def test_percentages(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointErrorDistribution()
        for _ in range(8):
            svc.record_error("inst-1", "/api", 429, "RATE_LIMITED")
        for _ in range(2):
            svc.record_error("inst-1", "/api", 500, "INTERNAL")
        dist = svc.get_distribution("inst-1", "/api")
        assert dist.buckets[0].percentage == 80.0

    def test_error_rate(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointErrorDistribution()
        for _ in range(100):
            svc.record_request("inst-1", "/api")
        for _ in range(5):
            svc.record_error("inst-1", "/api", 500, "ERR")
        assert svc.get_distribution("inst-1", "/api").error_rate_pct == 5.0

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointErrorDistribution()
        assert svc.get_distribution("inst-1", "/api").total_errors == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointErrorDistribution()
        svc.record_error("inst-1", "/api", 500, "ERR")
        assert svc.get_distribution("inst-2", "/api").total_errors == 0
