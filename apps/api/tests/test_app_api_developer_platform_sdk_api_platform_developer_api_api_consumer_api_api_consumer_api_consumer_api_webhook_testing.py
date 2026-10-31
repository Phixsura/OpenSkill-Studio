import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_webhook_testing import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTesting, TestPayload,
)

class TestConsumerApiWebhookTesting:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_send_test(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTesting()
        result = svc.send_test("inst-1", "c1", "https://hook.example.com", TestPayload(event_type="ping"), now=self._now())
        assert result.success and result.event_type == "ping"

    def test_custom_payload(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTesting()
        result = svc.send_test("inst-1", "c1", "https://hook.example.com", TestPayload(event_type="custom", payload={"key": "value"}), now=self._now())
        assert result.success and result.payload_size_bytes > 0

    def test_https_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTesting()
        with pytest.raises(ValueError, match="HTTPS"):
            svc.send_test("inst-1", "c1", "http://insecure.com", TestPayload(event_type="ping"), now=self._now())

    def test_standard_events(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTesting()
        events = svc.get_standard_events()
        assert "ping" in events and "order.created" in events

    def test_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTesting()
        svc.send_test("inst-1", "c1", "https://hook.example.com", TestPayload(event_type="ping"), now=self._now())
        assert len(svc.get_history("inst-1", "c1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTesting()
        svc.send_test("inst-1", "c1", "https://hook.example.com", TestPayload(event_type="ping"), now=self._now())
        assert len(svc.get_history("inst-2", "c1")) == 0
