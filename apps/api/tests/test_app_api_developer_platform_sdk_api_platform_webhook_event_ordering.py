from app.services.app_api_developer_platform_sdk_api_platform_webhook_event_ordering import AppAPIDeveloperPlatformSDKApiPlatformWebhookEventOrdering

class TestWebhookEventOrdering:
    def test_enqueue(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventOrdering()
        p = o.enqueue("inst-1", "user-123", "e1", 1)
        assert p.pending_count == 1

    def test_deliver(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventOrdering()
        o.enqueue("inst-1", "user-123", "e1", 1)
        p = o.deliver("inst-1", "user-123", 1)
        assert p.last_delivered_seq == 1
        assert p.pending_count == 0

    def test_out_of_order(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventOrdering()
        o.enqueue("inst-1", "user-123", "e1", 5)
        o.deliver("inst-1", "user-123", 5)
        o.enqueue("inst-1", "user-123", "e2", 3)  # older seq
        assert o.all_partitions("inst-1")[0].out_of_order_count == 1

    def test_out_of_order_list(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventOrdering()
        o.enqueue("inst-1", "p1", "e1", 1)
        o.enqueue("inst-1", "p2", "e2", 5)
        o.deliver("inst-1", "p2", 5)
        o.enqueue("inst-1", "p2", "e3", 2)  # out of order
        assert len(o.out_of_order_partitions("inst-1")) == 1

    def test_isolation(self):
        o = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventOrdering()
        o.enqueue("inst-1", "p1", "e1", 1)
        assert len(o.all_partitions("inst-2")) == 0
