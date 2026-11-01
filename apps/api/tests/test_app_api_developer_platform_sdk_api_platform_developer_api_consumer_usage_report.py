from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_usage_report import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerUsageReport

class TestConsumerUsageReport:
    def test_record_and_metrics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerUsageReport()
        svc.record("inst-1", "c1", "/api", 50.0, True, 1024)
        svc.record("inst-1", "c1", "/api", 100.0, False, 512)
        m = svc.get_metrics("inst-1", "c1")
        assert m.total_requests == 2
        assert m.success_rate == 50.0
        assert m.avg_latency_ms == 75.0

    def test_generate_report(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerUsageReport()
        svc.record("inst-1", "c1", "/api", 30.0, True)
        report = svc.generate_report("inst-1", "c1", "r1", "daily")
        assert report.metrics.total_requests == 1
        assert report.period == "daily"

    def test_empty_metrics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerUsageReport()
        m = svc.get_metrics("inst-1", "c1")
        assert m.success_rate == 0.0 and m.avg_latency_ms == 0.0

    def test_consumer_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerUsageReport()
        svc.record("inst-1", "c1", "/a", 10, True)
        svc.record("inst-1", "c2", "/a", 10, True)
        assert svc.consumer_count("inst-1") == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerUsageReport()
        svc.record("inst-1", "c1", "/api", 10, True)
        assert svc.consumer_count("inst-2") == 0
