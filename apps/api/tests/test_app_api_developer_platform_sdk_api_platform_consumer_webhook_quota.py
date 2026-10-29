import pytest
from app.services.app_api_developer_platform_sdk_api_platform_consumer_webhook_quota import AppAPIDeveloperPlatformSDKApiPlatformConsumerWebhookQuota

class TestConsumerWebhookQuota:
    def test_set_and_consume(self):
        q = AppAPIDeveloperPlatformSDKApiPlatformConsumerWebhookQuota()
        q.set_quota("inst-1", "c1", 1000)
        q.consume("inst-1", "c1", 500)
        wq = q.all_quotas("inst-1")[0]
        assert wq.remaining == 500
        assert wq.usage_pct == 50.0

    def test_exhausted(self):
        q = AppAPIDeveloperPlatformSDKApiPlatformConsumerWebhookQuota()
        q.set_quota("inst-1", "c1", 10)
        q.consume("inst-1", "c1", 10)
        assert len(q.exhausted_consumers("inst-1")) == 1

    def test_overage(self):
        q = AppAPIDeveloperPlatformSDKApiPlatformConsumerWebhookQuota()
        q.set_quota("inst-1", "c1", 10)
        q.consume("inst-1", "c1", 15)
        assert q.all_quotas("inst-1")[0].overage_count == 5

    def test_reset(self):
        q = AppAPIDeveloperPlatformSDKApiPlatformConsumerWebhookQuota()
        q.set_quota("inst-1", "c1", 100)
        q.consume("inst-1", "c1", 50)
        q.reset_daily("inst-1")
        assert q.all_quotas("inst-1")[0].used_today == 0

    def test_isolation(self):
        q = AppAPIDeveloperPlatformSDKApiPlatformConsumerWebhookQuota()
        q.set_quota("inst-1", "c1", 100)
        assert len(q.all_quotas("inst-2")) == 0
