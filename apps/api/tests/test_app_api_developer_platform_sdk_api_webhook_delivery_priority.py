from app.services.app_api_developer_platform_sdk_api_webhook_delivery_priority import AppAPIDeveloperPlatformSDKApiWebhookDeliveryPriority

class TestDeliveryPriority:
    def test_enqueue(self):
        p = AppAPIDeveloperPlatformSDKApiWebhookDeliveryPriority()
        q = p.enqueue("inst-1", "https://a.com", "critical", 5)
        assert q.queued["critical"] == 5

    def test_deliver(self):
        p = AppAPIDeveloperPlatformSDKApiWebhookDeliveryPriority()
        p.enqueue("inst-1", "https://a.com", "high", 10)
        q = p.deliver("inst-1", "https://a.com", "high", 3)
        assert q.queued["high"] == 7
        assert q.delivered["high"] == 3

    def test_next_priority(self):
        p = AppAPIDeveloperPlatformSDKApiWebhookDeliveryPriority()
        p.enqueue("inst-1", "https://a.com", "low", 5)
        p.enqueue("inst-1", "https://a.com", "critical", 1)
        assert p.next_priority("inst-1", "https://a.com") == "critical"

    def test_empty_queue(self):
        p = AppAPIDeveloperPlatformSDKApiWebhookDeliveryPriority()
        p.enqueue("inst-1", "https://a.com", "normal", 1)
        p.deliver("inst-1", "https://a.com", "normal", 1)
        assert p.next_priority("inst-1", "https://a.com") is None

    def test_isolation(self):
        p = AppAPIDeveloperPlatformSDKApiWebhookDeliveryPriority()
        p.enqueue("inst-1", "https://a.com", "normal", 10)
        assert len(p.all_queues("inst-2")) == 0
