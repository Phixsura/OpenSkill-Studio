import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_webhook_retry_strategy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy, RetryStrategy,
)

class TestWebhookRetryStrategy:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_exponential(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy()
        svc.set_strategy("inst-1", "c1", RetryStrategy(strategy_id="s1", webhook_id="w1", base_delay_seconds=10, multiplier=2.0))
        assert svc.compute_delay("inst-1", "c1", "w1", 1) == 10
        assert svc.compute_delay("inst-1", "c1", "w1", 2) == 20
        assert svc.compute_delay("inst-1", "c1", "w1", 3) == 40

    def test_linear(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy()
        svc.set_strategy("inst-1", "c1", RetryStrategy(strategy_id="s1", webhook_id="w1", strategy_type="linear", base_delay_seconds=30))
        assert svc.compute_delay("inst-1", "c1", "w1", 1) == 30
        assert svc.compute_delay("inst-1", "c1", "w1", 3) == 90

    def test_fixed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy()
        svc.set_strategy("inst-1", "c1", RetryStrategy(strategy_id="s1", webhook_id="w1", strategy_type="fixed", base_delay_seconds=60))
        assert svc.compute_delay("inst-1", "c1", "w1", 1) == 60
        assert svc.compute_delay("inst-1", "c1", "w1", 5) == 60

    def test_max_delay_cap(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy()
        svc.set_strategy("inst-1", "c1", RetryStrategy(strategy_id="s1", webhook_id="w1", base_delay_seconds=100, multiplier=10, max_delay_seconds=500))
        assert svc.compute_delay("inst-1", "c1", "w1", 3) == 500  # capped

    def test_give_up_after_max(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy()
        svc.set_strategy("inst-1", "c1", RetryStrategy(strategy_id="s1", webhook_id="w1", max_retries=3))
        assert svc.compute_delay("inst-1", "c1", "w1", 4) == -1

    def test_schedule(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy()
        svc.set_strategy("inst-1", "c1", RetryStrategy(strategy_id="s1", webhook_id="w1", max_retries=3, base_delay_seconds=10, multiplier=2.0))
        schedule = svc.get_schedule("inst-1", "c1", "w1", self._now())
        assert len(schedule) == 3 and schedule[0].delay_seconds == 10

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy()
        svc.set_strategy("inst-1", "c1", RetryStrategy(strategy_id="s1", webhook_id="w1", base_delay_seconds=60))
        assert svc.get_strategy("inst-2", "c1", "w1") is None
