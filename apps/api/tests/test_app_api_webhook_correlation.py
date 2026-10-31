from app.services.app_api_webhook_correlation import AppAPIWebhookCorrelation

class TestCorrelation:
    def test_start(self):
        c = AppAPIWebhookCorrelation()
        e = c.start("inst-1", "c1", "push", "https://a.com")
        assert e.round_trip_ms is None

    def test_complete(self):
        c = AppAPIWebhookCorrelation()
        c.start("inst-1", "c1", "push", "https://a.com")
        e = c.complete("inst-1", "c1", 200)
        assert e.status_code == 200
        assert e.round_trip_ms is not None

    def test_pending(self):
        c = AppAPIWebhookCorrelation()
        c.start("inst-1", "c1", "push", "https://a.com")
        c.start("inst-1", "c2", "issue", "https://b.com")
        c.complete("inst-1", "c1", 200)
        assert len(c.pending("inst-1")) == 1

    def test_isolation(self):
        c = AppAPIWebhookCorrelation()
        c.start("inst-1", "c1", "push", "https://a.com")
        assert c.list_entries("inst-2") == []
