import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_webhook_delivery_window import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindow, DeliveryWindow,
)

class TestWebhookDeliveryWindow:
    def test_within_window(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(window_id="w1", webhook_id="wh1", consumer_id="c1", start_hour=9, end_hour=17, days_of_week=[0, 1, 2, 3, 4]))
        result = svc.check("inst-1", "c1", "wh1", datetime(2026, 6, 1, 10, 0))
        assert result.allowed

    def test_outside_hours(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(window_id="w1", webhook_id="wh1", consumer_id="c1", start_hour=9, end_hour=17))
        assert not svc.check("inst-1", "c1", "wh1", datetime(2026, 6, 1, 20, 0)).allowed

    def test_outside_day(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(window_id="w1", webhook_id="wh1", consumer_id="c1", start_hour=0, end_hour=23, days_of_week=[0, 1, 2, 3, 4]))
        assert not svc.check("inst-1", "c1", "wh1", datetime(2026, 6, 6, 10, 0)).allowed

    def test_overnight(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(window_id="w1", webhook_id="wh1", consumer_id="c1", start_hour=22, end_hour=6))
        assert svc.check("inst-1", "c1", "wh1", datetime(2026, 6, 1, 23, 0)).allowed
        assert not svc.check("inst-1", "c1", "wh1", datetime(2026, 6, 1, 12, 0)).allowed

    def test_no_window(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindow()
        assert svc.check("inst-1", "c1", "wh1", datetime(2026, 6, 1, 3, 0)).allowed

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindow()
        svc.set_window("inst-1", DeliveryWindow(window_id="w1", webhook_id="wh1", consumer_id="c1", start_hour=9, end_hour=17))
        assert svc.get_window("inst-2", "c1", "wh1") is None
