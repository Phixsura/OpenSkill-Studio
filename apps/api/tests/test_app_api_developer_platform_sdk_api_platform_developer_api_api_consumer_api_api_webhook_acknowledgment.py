from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_acknowledgment import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookAcknowledgment

class TestWebhookAcknowledgment:
    def test_deliver_and_ack(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookAcknowledgment()
        svc.record_delivery("inst-1", "ev1", "c1")
        rec = svc.acknowledge("inst-1", "c1", "ev1")
        assert rec.acknowledged is True
        assert rec.ack_latency_ms >= 0

    def test_ack_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookAcknowledgment()
        svc.record_delivery("inst-1", "ev1", "c1")
        svc.record_delivery("inst-1", "ev2", "c1")
        svc.acknowledge("inst-1", "c1", "ev1")
        assert svc.ack_rate("inst-1") == 50.0

    def test_unknown_event(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookAcknowledgment()
        import pytest
        with pytest.raises(KeyError):
            svc.acknowledge("inst-1", "c1", "nope")

    def test_idempotent_ack(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookAcknowledgment()
        svc.record_delivery("inst-1", "ev1", "c1")
        svc.acknowledge("inst-1", "c1", "ev1")
        rec = svc.acknowledge("inst-1", "c1", "ev1")  # double ack
        assert rec.acknowledged is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookAcknowledgment()
        svc.record_delivery("inst-1", "ev1", "c1")
        assert svc.ack_rate("inst-2") == 0.0
