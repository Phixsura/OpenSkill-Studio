import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_usage_comparison import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparison, ConsumerUsage,
)

class TestUsageComparison:
    def test_compare(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparison()
        svc.set_usage("inst-1", ConsumerUsage(consumer_id="c1", requests=5000, errors=10, avg_latency_ms=50, active_keys=3, active_webhooks=2))
        svc.set_usage("inst-1", ConsumerUsage(consumer_id="c2", requests=1000, errors=5, avg_latency_ms=80, active_keys=1, active_webhooks=1))
        result = svc.compare("inst-1")
        assert result.highest_usage == "c1" and result.lowest_usage == "c2" and result.total_requests == 6000

    def test_filter_by_ids(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparison()
        svc.set_usage("inst-1", ConsumerUsage(consumer_id="c1", requests=5000, errors=0, avg_latency_ms=50, active_keys=1, active_webhooks=0))
        svc.set_usage("inst-1", ConsumerUsage(consumer_id="c2", requests=3000, errors=0, avg_latency_ms=60, active_keys=1, active_webhooks=0))
        svc.set_usage("inst-1", ConsumerUsage(consumer_id="c3", requests=1000, errors=0, avg_latency_ms=70, active_keys=1, active_webhooks=0))
        result = svc.compare("inst-1", consumer_ids=["c1", "c3"])
        assert len(result.consumers) == 2

    def test_rank_by_errors(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparison()
        svc.set_usage("inst-1", ConsumerUsage(consumer_id="c1", requests=1000, errors=5, avg_latency_ms=50, active_keys=1, active_webhooks=0))
        svc.set_usage("inst-1", ConsumerUsage(consumer_id="c2", requests=500, errors=50, avg_latency_ms=50, active_keys=1, active_webhooks=0))
        ranked = svc.rank_by_metric("inst-1", "errors")
        assert ranked[0].consumer_id == "c2"

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparison()
        result = svc.compare("inst-1")
        assert result.total_requests == 0

    def test_negative_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparison()
        with pytest.raises(ValueError, match="non-negative"):
            svc.set_usage("inst-1", ConsumerUsage(consumer_id="c1", requests=-1, errors=0, avg_latency_ms=0, active_keys=0, active_webhooks=0))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiUsageComparison()
        svc.set_usage("inst-1", ConsumerUsage(consumer_id="c1", requests=100, errors=0, avg_latency_ms=50, active_keys=1, active_webhooks=0))
        assert svc.compare("inst-2").total_requests == 0
