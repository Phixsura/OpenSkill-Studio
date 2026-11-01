from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_usage_summary import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageSummary, ConsumerUsageSummary,
)

class TestConsumerApiUsageSummary:
    def test_success_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageSummary()
        svc.update("inst-1", ConsumerUsageSummary(consumer_id="c1", total_requests=1000, successful=950, failed=50))
        s = svc.get_summary("inst-1", "c1")
        assert s.success_rate == 95.0

    def test_data_total(self):
        s = ConsumerUsageSummary(consumer_id="c1", data_in_bytes=1048576, data_out_bytes=2097152)
        assert s.data_total_mb == 3.0

    def test_top_by_requests(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageSummary()
        svc.update("inst-1", ConsumerUsageSummary(consumer_id="c1", total_requests=100))
        svc.update("inst-1", ConsumerUsageSummary(consumer_id="c2", total_requests=5000))
        top = svc.top_by_requests("inst-1", 1)
        assert top[0].consumer_id == "c2"

    def test_low_success_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageSummary()
        svc.update("inst-1", ConsumerUsageSummary(consumer_id="c1", total_requests=100, successful=80, failed=20))
        assert len(svc.low_success_rate("inst-1", 95)) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageSummary()
        svc.update("inst-1", ConsumerUsageSummary(consumer_id="c1"))
        assert len(svc.list_summaries("inst-2")) == 0
