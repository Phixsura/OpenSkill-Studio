import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_usage_heatmap import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmap,
)

class TestConsumerApiUsageHeatmap:
    def test_record_and_heatmap(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmap()
        # Monday at 10am
        ts = datetime(2026, 6, 1, 10, 0, 0)  # Monday
        for _ in range(5):
            svc.record("inst-1", "c1", ts, latency_ms=50)
        heatmap = svc.get_heatmap("inst-1", "c1")
        assert heatmap.total_requests == 5 and heatmap.peak_hour == 10

    def test_error_tracking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmap()
        ts = datetime(2026, 6, 1, 14, 0, 0)
        svc.record("inst-1", "c1", ts, is_error=True)
        svc.record("inst-1", "c1", ts, is_error=False)
        heatmap = svc.get_heatmap("inst-1", "c1")
        bucket = [b for b in heatmap.buckets if b.hour == 14][0]
        assert bucket.error_count == 1 and bucket.request_count == 2

    def test_running_avg_latency(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmap()
        ts = datetime(2026, 6, 1, 9, 0, 0)
        svc.record("inst-1", "c1", ts, latency_ms=100)
        svc.record("inst-1", "c1", ts, latency_ms=200)
        heatmap = svc.get_heatmap("inst-1", "c1")
        bucket = [b for b in heatmap.buckets if b.hour == 9][0]
        assert 149 < bucket.avg_latency_ms < 151  # ~150

    def test_peak_hours(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmap()
        for _ in range(10):
            svc.record("inst-1", "c1", datetime(2026, 6, 1, 10, 0))
        for _ in range(5):
            svc.record("inst-1", "c1", datetime(2026, 6, 1, 14, 0))
        peaks = svc.get_peak_hours("inst-1", "c1", top_n=2)
        assert peaks[0].hour == 10 and peaks[0].request_count == 10

    def test_empty_heatmap(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmap()
        heatmap = svc.get_heatmap("inst-1", "c1")
        assert heatmap.total_requests == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmap()
        svc.record("inst-1", "c1", datetime(2026, 6, 1, 10, 0))
        assert svc.get_heatmap("inst-2", "c1").total_requests == 0
