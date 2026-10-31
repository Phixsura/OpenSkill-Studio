import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_api_consumer_api_api_consumer_api_api_consumer_api_quota_usage_summary import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummary,
)

class TestQuotaUsageSummary:
    def test_all_ok(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummary()
        svc.set_usage("inst-1", "c1", "api_keys", 3, 10)
        svc.set_usage("inst-1", "c1", "webhooks", 2, 5)
        summary = svc.get_summary("inst-1", "c1")
        assert summary.overall_status == "ok" and summary.at_risk_count == 0

    def test_warning(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummary()
        svc.set_usage("inst-1", "c1", "api_keys", 9, 10)
        summary = svc.get_summary("inst-1", "c1")
        assert summary.overall_status == "warning" and summary.quotas[0].status == "warning"

    def test_exceeded(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummary()
        svc.set_usage("inst-1", "c1", "api_keys", 15, 10)
        summary = svc.get_summary("inst-1", "c1")
        assert summary.overall_status == "exceeded"

    def test_sorted_by_usage(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummary()
        svc.set_usage("inst-1", "c1", "low", 1, 100)
        svc.set_usage("inst-1", "c1", "high", 95, 100)
        summary = svc.get_summary("inst-1", "c1")
        assert summary.quotas[0].resource == "high"

    def test_negative_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummary()
        with pytest.raises(ValueError, match="non-negative"):
            svc.set_usage("inst-1", "c1", "x", -1, 10)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiQuotaUsageSummary()
        svc.set_usage("inst-1", "c1", "x", 5, 10)
        assert svc.get_summary("inst-2", "c1").total_resources == 0
