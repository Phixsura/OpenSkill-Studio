import pytest
from app.services.app_api_developer_platform_sdk_api_webhook_retry_budget import AppAPIDeveloperPlatformSDKApiWebhookRetryBudget

class TestRetryBudget:
    def test_set_budget(self):
        b = AppAPIDeveloperPlatformSDKApiWebhookRetryBudget()
        r = b.set_budget("inst-1", "https://a.com", 100)
        assert r.remaining == 100

    def test_use_retry(self):
        b = AppAPIDeveloperPlatformSDKApiWebhookRetryBudget()
        b.set_budget("inst-1", "https://a.com", 10)
        b.use_retry("inst-1", "https://a.com")
        r = b.all_budgets("inst-1")[0]
        assert r.remaining == 9
        assert r.usage_pct == 10.0

    def test_exhausted(self):
        b = AppAPIDeveloperPlatformSDKApiWebhookRetryBudget()
        b.set_budget("inst-1", "https://a.com", 2)
        b.use_retry("inst-1", "https://a.com")
        b.use_retry("inst-1", "https://a.com")
        with pytest.raises(ValueError, match="exhausted"):
            b.use_retry("inst-1", "https://a.com")

    def test_reset(self):
        b = AppAPIDeveloperPlatformSDKApiWebhookRetryBudget()
        b.set_budget("inst-1", "https://a.com", 10)
        for _ in range(5): b.use_retry("inst-1", "https://a.com")
        b.reset("inst-1", "https://a.com")
        assert b.all_budgets("inst-1")[0].remaining == 10

    def test_isolation(self):
        b = AppAPIDeveloperPlatformSDKApiWebhookRetryBudget()
        b.set_budget("inst-1", "https://a.com", 100)
        assert len(b.all_budgets("inst-2")) == 0
