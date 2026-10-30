from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_log_aggregator import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestLogAggregator

class TestRequestLogAggregator:
    def test_record_and_aggregate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestLogAggregator()
        svc.record("inst-1", "2024-01-15T14:00", "c1", 50.0)
        svc.record("inst-1", "2024-01-15T14:00", "c2", 100.0, error=True)
        b = svc.get_bucket("inst-1", "2024-01-15T14:00")
        assert b.request_count == 2
        assert b.avg_latency == 75.0
        assert b.error_rate == 50.0
        assert len(b.unique_consumers) == 2

    def test_peak_bucket(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestLogAggregator()
        for _ in range(100): svc.record("inst-1", "peak-hour", "c1", 10)
        for _ in range(10): svc.record("inst-1", "quiet-hour", "c1", 10)
        peak = svc.peak_bucket("inst-1")
        assert peak.bucket_key == "peak-hour"

    def test_recent_sorted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestLogAggregator()
        svc.record("inst-1", "2024-01-15T15:00", "c1", 10)
        svc.record("inst-1", "2024-01-15T14:00", "c1", 10)
        recent = svc.recent_buckets("inst-1")
        assert recent[0].bucket_key == "2024-01-15T14:00"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestLogAggregator()
        svc.record("inst-1", "2024-01-15T14:00", "c1", 10)
        assert svc.total_requests("inst-2") == 0
