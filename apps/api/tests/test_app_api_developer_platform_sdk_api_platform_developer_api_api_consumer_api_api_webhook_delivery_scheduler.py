import pytest, time
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_delivery_scheduler import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryScheduler, ScheduledDelivery,
)

class TestWebhookDeliveryScheduler:
    def test_schedule(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryScheduler()
        d = svc.schedule("inst-1", ScheduledDelivery(delivery_id="d1", event_id="e1", consumer_id="c1", deliver_at=time.time() + 3600))
        assert d.delivered is False
        assert svc.pending_count("inst-1") == 1

    def test_due_deliveries(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryScheduler()
        svc.schedule("inst-1", ScheduledDelivery(delivery_id="d1", event_id="e1", consumer_id="c1", deliver_at=time.time() + 3600))
        # Manually set to past
        svc._scheduled[("inst-1", "d1")].deliver_at = time.time() - 1
        assert len(svc.due_deliveries("inst-1")) == 1

    def test_mark_delivered(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryScheduler()
        svc.schedule("inst-1", ScheduledDelivery(delivery_id="d1", event_id="e1", consumer_id="c1", deliver_at=time.time() + 100))
        svc.mark_delivered("inst-1", "d1")
        assert svc.pending_count("inst-1") == 0

    def test_cancel(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryScheduler()
        svc.schedule("inst-1", ScheduledDelivery(delivery_id="d1", event_id="e1", consumer_id="c1", deliver_at=time.time() + 100))
        assert svc.cancel("inst-1", "d1") is True
        assert svc.pending_count("inst-1") == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryScheduler()
        svc.schedule("inst-1", ScheduledDelivery(delivery_id="d1", event_id="e1", consumer_id="c1", deliver_at=time.time() + 100))
        assert len(svc.list_scheduled("inst-2")) == 0
