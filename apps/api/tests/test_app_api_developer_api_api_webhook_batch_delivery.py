from app.services.app_api_developer_api_api_webhook_batch_delivery import AppAPIDeveloperAPIApiWebhookBatchDelivery

class TestBatchDelivery:
    def test_configure(self):
        b = AppAPIDeveloperAPIApiWebhookBatchDelivery()
        c = b.configure("inst-1", "https://a.com", 10, 5000)
        assert c.max_batch_size == 10

    def test_batch_on_size(self):
        b = AppAPIDeveloperAPIApiWebhookBatchDelivery()
        b.configure("inst-1", "https://a.com", 3, 5000)
        assert b.add_event("inst-1", "https://a.com", "e1") is None
        assert b.add_event("inst-1", "https://a.com", "e2") is None
        result = b.add_event("inst-1", "https://a.com", "e3")
        assert result is not None
        assert result.event_count == 3

    def test_manual_flush(self):
        b = AppAPIDeveloperAPIApiWebhookBatchDelivery()
        b.configure("inst-1", "https://a.com", 100, 5000)
        b.add_event("inst-1", "https://a.com", "e1")
        result = b.flush("inst-1", "https://a.com")
        assert result is not None
        assert result.event_count == 1

    def test_stats(self):
        b = AppAPIDeveloperAPIApiWebhookBatchDelivery()
        b.configure("inst-1", "https://a.com", 2, 1000)
        b.add_event("inst-1", "https://a.com", "e1")
        b.add_event("inst-1", "https://a.com", "e2")
        b.add_event("inst-1", "https://a.com", "e3")
        s = b.stats("inst-1")
        assert s["batches_sent"] == 1
        assert s["events_batched"] == 3
        assert s["pending"] == 1

    def test_isolation(self):
        b = AppAPIDeveloperAPIApiWebhookBatchDelivery()
        b.configure("inst-1", "https://a.com", 10, 1000)
        assert b.stats("inst-2")["batches_sent"] == 0
