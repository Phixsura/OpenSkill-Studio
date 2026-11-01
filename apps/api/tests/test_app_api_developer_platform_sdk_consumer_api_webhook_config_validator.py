import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_webhook_config_validator import (
    AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator, WebhookConfig,
)

class TestWebhookConfigValidator:
    def test_perfect_config(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator()
        result = svc.validate(WebhookConfig(webhook_id="w1", url="https://hook.example.com/events", secret="a" * 32, events=["order.created"], timeout_ms=30000, retry_count=3))
        assert result.valid and result.score == 100

    def test_http_rejected(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator()
        result = svc.validate(WebhookConfig(webhook_id="w1", url="http://insecure.com"))
        assert not result.valid and any("HTTPS" in i.message for i in result.issues)

    def test_no_secret_warning(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator()
        result = svc.validate(WebhookConfig(webhook_id="w1", url="https://hook.example.com", events=["x"]))
        assert result.valid and result.score < 100 and any("secret" in i.message.lower() for i in result.issues)

    def test_short_secret_warning(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator()
        result = svc.validate(WebhookConfig(webhook_id="w1", url="https://hook.example.com", secret="short", events=["x"]))
        assert any("32 characters" in i.message for i in result.issues)

    def test_no_retries_warning(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator()
        result = svc.validate(WebhookConfig(webhook_id="w1", url="https://hook.example.com", secret="a" * 32, events=["x"], retry_count=0))
        assert any("retries" in i.message.lower() for i in result.issues)

    def test_empty_url(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator()
        result = svc.validate(WebhookConfig(webhook_id="w1", url=""))
        assert not result.valid

    def test_low_timeout_warning(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator()
        result = svc.validate(WebhookConfig(webhook_id="w1", url="https://x.com", secret="a" * 32, events=["x"], timeout_ms=2000))
        assert any("5s" in i.message for i in result.issues)
