from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_delivery_confirmation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryConfirmation, DeliveryConfirmation, ConfirmationStatus,
)

class TestWebhookDeliveryConfirmation:
    def test_deliver_and_confirm(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryConfirmation()
        svc.record_delivery("inst-1", DeliveryConfirmation(delivery_id="d1", event_id="e1", consumer_id="c1"))
        d = svc.confirm("inst-1", "d1")
        assert d.status == ConfirmationStatus.CONFIRMED

    def test_double_confirm_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryConfirmation()
        svc.record_delivery("inst-1", DeliveryConfirmation(delivery_id="d1", event_id="e1", consumer_id="c1"))
        svc.confirm("inst-1", "d1")
        import pytest
        with pytest.raises(ValueError, match="confirmed"):
            svc.confirm("inst-1", "d1")

    def test_timeout_detection(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryConfirmation()
        svc.record_delivery("inst-1", DeliveryConfirmation(delivery_id="d1", event_id="e1", consumer_id="c1", timeout_s=0))
        import time; time.sleep(0.01)
        timed_out = svc.check_timeouts("inst-1")
        assert len(timed_out) == 1

    def test_confirmation_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryConfirmation()
        svc.record_delivery("inst-1", DeliveryConfirmation(delivery_id="d1", event_id="e1", consumer_id="c1"))
        svc.confirm("inst-1", "d1")
        svc.record_delivery("inst-1", DeliveryConfirmation(delivery_id="d2", event_id="e2", consumer_id="c1", timeout_s=0))
        import time; time.sleep(0.01)
        svc.check_timeouts("inst-1")
        assert svc.confirmation_rate("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryConfirmation()
        svc.record_delivery("inst-1", DeliveryConfirmation(delivery_id="d1", event_id="e1", consumer_id="c1"))
        assert svc.pending_count("inst-2") == 0
