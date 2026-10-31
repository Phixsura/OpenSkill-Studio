import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_webhook_retry_policy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookRetryPolicy, RetryPolicy, RetryStrategy,
)

class TestWebhookRetryPolicy:
    def test_exponential_delay(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookRetryPolicy()
        p = RetryPolicy(policy_id="p1", consumer_id="c1", strategy=RetryStrategy.EXPONENTIAL, base_delay_s=10, max_delay_s=3600)
        svc.set_policy("inst-1", p)
        assert p.delay_for_attempt(1) == 10
        assert p.delay_for_attempt(2) == 20
        assert p.delay_for_attempt(3) == 40

    def test_fixed_delay(self):
        p = RetryPolicy(policy_id="p1", consumer_id="c1", strategy=RetryStrategy.FIXED, base_delay_s=30)
        assert p.delay_for_attempt(1) == 30
        assert p.delay_for_attempt(5) == 30

    def test_max_delay_cap(self):
        p = RetryPolicy(policy_id="p1", consumer_id="c1", strategy=RetryStrategy.EXPONENTIAL, base_delay_s=100, max_delay_s=500)
        assert p.delay_for_attempt(10) == 500  # capped

    def test_record_attempt(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookRetryPolicy()
        svc.set_policy("inst-1", RetryPolicy(policy_id="p1", consumer_id="c1", max_retries=3))
        da = svc.record_attempt("inst-1", "c1", "ev1", 1, 500)
        assert da.success is False
        assert da.next_retry_delay_s > 0

    def test_should_retry(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookRetryPolicy()
        svc.set_policy("inst-1", RetryPolicy(policy_id="p1", consumer_id="c1", max_retries=3))
        assert svc.should_retry("inst-1", "c1", 2) is True
        assert svc.should_retry("inst-1", "c1", 3) is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookRetryPolicy()
        svc.set_policy("inst-1", RetryPolicy(policy_id="p1", consumer_id="c1"))
        assert len(svc.list_policies("inst-2")) == 0
