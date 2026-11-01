import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_webhook_circuit_breaker import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookCircuitBreaker, WebhookCircuitConfig,
)

class TestConsumerApiWebhookCircuitBreaker:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_closed_delivers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookCircuitBreaker()
        svc.configure("inst-1", WebhookCircuitConfig(webhook_id="w1", consumer_id="c1", failure_threshold=3))
        assert svc.should_deliver("inst-1", "c1", "w1", self._now())

    def test_opens_after_failures(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookCircuitBreaker()
        svc.configure("inst-1", WebhookCircuitConfig(webhook_id="w1", consumer_id="c1", failure_threshold=3))
        for _ in range(3):
            svc.record_failure("inst-1", "c1", "w1", self._now())
        assert not svc.should_deliver("inst-1", "c1", "w1", self._now())

    def test_half_open_after_timeout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookCircuitBreaker()
        svc.configure("inst-1", WebhookCircuitConfig(webhook_id="w1", consumer_id="c1", failure_threshold=2, timeout_seconds=30))
        svc.record_failure("inst-1", "c1", "w1", self._now())
        svc.record_failure("inst-1", "c1", "w1", self._now())
        assert svc.should_deliver("inst-1", "c1", "w1", self._now() + timedelta(seconds=35))
        assert svc.get_state("inst-1", "c1", "w1").state == "half_open"

    def test_closes_after_successes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookCircuitBreaker()
        svc.configure("inst-1", WebhookCircuitConfig(webhook_id="w1", consumer_id="c1", failure_threshold=2, success_threshold=2, timeout_seconds=10))
        svc.record_failure("inst-1", "c1", "w1", self._now())
        svc.record_failure("inst-1", "c1", "w1", self._now())
        svc.should_deliver("inst-1", "c1", "w1", self._now() + timedelta(seconds=15))
        svc.record_success("inst-1", "c1", "w1")
        svc.record_success("inst-1", "c1", "w1")
        assert svc.get_state("inst-1", "c1", "w1").state == "closed"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookCircuitBreaker()
        svc.configure("inst-1", WebhookCircuitConfig(webhook_id="w1", consumer_id="c1", failure_threshold=1))
        svc.record_failure("inst-1", "c1", "w1", self._now())
        assert svc.should_deliver("inst-2", "c1", "w1", self._now())
