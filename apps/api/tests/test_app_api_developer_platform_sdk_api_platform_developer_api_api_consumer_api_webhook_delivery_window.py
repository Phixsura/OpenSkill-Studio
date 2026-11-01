import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_delivery_window import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookDeliveryWindow, DeliveryWindow,
)

class TestWebhookDeliveryWindow:
    def test_in_window(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(consumer_id="c1", start_hour=9, end_hour=17))
        assert svc.is_in_window("inst-1", "c1", 12, "mon") is True
        assert svc.is_in_window("inst-1", "c1", 20, "mon") is False

    def test_midnight_wrap(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(consumer_id="c1", start_hour=22, end_hour=6))
        assert svc.is_in_window("inst-1", "c1", 23, "tue") is True
        assert svc.is_in_window("inst-1", "c1", 3, "tue") is True
        assert svc.is_in_window("inst-1", "c1", 12, "tue") is False

    def test_day_restriction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(consumer_id="c1", start_hour=9, end_hour=17, days=["mon", "tue", "wed", "thu", "fri"]))
        assert svc.is_in_window("inst-1", "c1", 12, "sat") is False

    def test_no_window_always_delivers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookDeliveryWindow()
        assert svc.is_in_window("inst-1", "c1", 3, "sun") is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(consumer_id="c1", start_hour=9, end_hour=17))
        assert len(svc.list_windows("inst-2")) == 0
