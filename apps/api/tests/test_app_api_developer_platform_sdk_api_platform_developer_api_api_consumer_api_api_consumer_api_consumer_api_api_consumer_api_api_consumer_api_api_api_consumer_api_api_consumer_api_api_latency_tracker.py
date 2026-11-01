import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_api_consumer_api_api_latency_tracker import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTracker,
)

class TestLatencyTracker:
    def test_percentiles(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTracker()
        for i in range(100):
            svc.record("inst-1", "c1", float(i + 1))
        dist = svc.get_distribution("inst-1", "c1")
        assert dist.p50_ms == 51.0  # index 50
        assert dist.total_requests == 100

    def test_buckets(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTracker()
        svc.record("inst-1", "c1", 20)
        svc.record("inst-1", "c1", 75)
        svc.record("inst-1", "c1", 250)
        svc.record("inst-1", "c1", 750)
        svc.record("inst-1", "c1", 2000)
        dist = svc.get_distribution("inst-1", "c1")
        assert dist.buckets[0].count == 1  # <50ms
        assert dist.buckets[4].count == 1  # >1s

    def test_average(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTracker()
        svc.record("inst-1", "c1", 100)
        svc.record("inst-1", "c1", 200)
        dist = svc.get_distribution("inst-1", "c1")
        assert dist.avg_ms == 150.0

    def test_negative_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTracker()
        with pytest.raises(ValueError, match="non-negative"):
            svc.record("inst-1", "c1", -5)

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTracker()
        dist = svc.get_distribution("inst-1", "c1")
        assert dist.total_requests == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTracker()
        svc.record("inst-1", "c1", 50)
        assert svc.get_distribution("inst-2", "c1").total_requests == 0
