from app.services.app_api_webhook_payload_size import AppAPIWebhookPayloadSize

class TestPayloadSize:
    def test_record(self):
        p = AppAPIWebhookPayloadSize(max_payload_bytes=1024)
        s = p.record("inst-1", "https://a.com", 500)
        assert s.delivery_count == 1
        assert s.avg_bytes == 500.0

    def test_over_limit(self):
        p = AppAPIWebhookPayloadSize(max_payload_bytes=1024)
        p.record("inst-1", "https://a.com", 2000)
        s = p.list_stats("inst-1")[0]
        assert s.over_limit_count == 1

    def test_max_tracked(self):
        p = AppAPIWebhookPayloadSize()
        p.record("inst-1", "https://a.com", 100)
        p.record("inst-1", "https://a.com", 500)
        assert p.list_stats("inst-1")[0].max_bytes == 500

    def test_isolation(self):
        p = AppAPIWebhookPayloadSize()
        p.record("inst-1", "https://a.com", 100)
        assert p.list_stats("inst-2") == []
