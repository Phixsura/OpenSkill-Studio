import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_consumer_api_consumer_api_consumer_api_webhook_rate_limiter import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiter, WebhookRateLimitConfig,
)

class TestWebhookRateLimiter:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_within_limit(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", WebhookRateLimitConfig(webhook_id="w1", consumer_id="c1", max_per_second=10))
        result = svc.check_and_consume("inst-1", "c1", "w1", self._now())
        assert result.allowed

    def test_second_limit(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", WebhookRateLimitConfig(webhook_id="w1", consumer_id="c1", max_per_second=3))
        for _ in range(3):
            svc.check_and_consume("inst-1", "c1", "w1", self._now())
        result = svc.check_and_consume("inst-1", "c1", "w1", self._now())
        assert not result.allowed and result.retry_after_ms == 1000

    def test_burst(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", WebhookRateLimitConfig(webhook_id="w1", consumer_id="c1", max_per_second=2, burst_size=3))
        for _ in range(5):
            svc.check_and_consume("inst-1", "c1", "w1", self._now())  # 2+3=5 allowed
        result = svc.check_and_consume("inst-1", "c1", "w1", self._now())
        assert not result.allowed

    def test_minute_limit(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", WebhookRateLimitConfig(webhook_id="w1", consumer_id="c1", max_per_second=100, max_per_minute=3))
        for _ in range(3):
            svc.check_and_consume("inst-1", "c1", "w1", self._now())
        result = svc.check_and_consume("inst-1", "c1", "w1", self._now())
        assert not result.allowed and result.retry_after_ms == 60000

    def test_default_config(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiter()
        result = svc.check_and_consume("inst-1", "c1", "unconfigured", self._now())
        assert result.allowed

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiter()
        svc.configure("inst-1", WebhookRateLimitConfig(webhook_id="w1", consumer_id="c1", max_per_second=1))
        svc.check_and_consume("inst-1", "c1", "w1", self._now())
        assert svc.check_and_consume("inst-2", "c1", "w1", self._now()).allowed
