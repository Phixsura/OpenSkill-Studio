import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_retry_budget import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookRetryBudget, RetryBudgetConfig, RetryRecord,
)

class TestWebhookRetryBudget:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_within_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookRetryBudget()
        svc.set_config("inst-1", RetryBudgetConfig(consumer_id="c1", max_retries_per_hour=10))
        svc.record_retry("inst-1", "c1", RetryRecord(webhook_id="w1", attempt=1, timestamp=self._now(), success=False))
        status = svc.check_budget("inst-1", "c1", self._now())
        assert not status.exhausted and status.hourly_used == 1

    def test_exhausted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookRetryBudget()
        svc.set_config("inst-1", RetryBudgetConfig(consumer_id="c1", max_retries_per_hour=3))
        for i in range(3):
            svc.record_retry("inst-1", "c1", RetryRecord(webhook_id=f"w{i}", attempt=1, timestamp=self._now(), success=False))
        status = svc.check_budget("inst-1", "c1", self._now())
        assert status.exhausted and status.cooldown_until is not None

    def test_old_records_expire(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookRetryBudget()
        svc.set_config("inst-1", RetryBudgetConfig(consumer_id="c1", max_retries_per_hour=5))
        old = self._now() - timedelta(hours=2)
        for i in range(5):
            svc.record_retry("inst-1", "c1", RetryRecord(webhook_id=f"w{i}", attempt=1, timestamp=old, success=False))
        status = svc.check_budget("inst-1", "c1", self._now())
        assert not status.exhausted and status.hourly_used == 0

    def test_success_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookRetryBudget()
        svc.record_retry("inst-1", "c1", RetryRecord(webhook_id="w1", attempt=1, timestamp=self._now(), success=True))
        svc.record_retry("inst-1", "c1", RetryRecord(webhook_id="w2", attempt=1, timestamp=self._now(), success=False))
        assert svc.success_rate("inst-1", "c1") == 0.5

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookRetryBudget()
        svc.record_retry("inst-1", "c1", RetryRecord(webhook_id="w1", attempt=1, timestamp=self._now(), success=False))
        assert svc.success_rate("inst-2", "c1") == 1.0
