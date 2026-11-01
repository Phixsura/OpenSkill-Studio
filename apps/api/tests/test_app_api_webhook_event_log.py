from app.services.app_api_webhook_event_log import AppAPIWebhookEventLog

class TestEventLog:
    def test_log(self):
        l = AppAPIWebhookEventLog()
        e = l.log_event("inst-1", "e1", "push", 3, 1024)
        assert e.destination_count == 3

    def test_recent(self):
        l = AppAPIWebhookEventLog()
        for i in range(5): l.log_event("inst-1", f"e{i}", "push", 1, 100)
        r = l.recent("inst-1", 3)
        assert len(r) == 3
        assert r[0].event_id == "e4"

    def test_by_type(self):
        l = AppAPIWebhookEventLog()
        l.log_event("inst-1", "e1", "push", 1, 100)
        l.log_event("inst-1", "e2", "issue", 1, 100)
        assert len(l.by_type("inst-1", "push")) == 1

    def test_isolation(self):
        l = AppAPIWebhookEventLog()
        l.log_event("inst-1", "e1", "push", 1, 100)
        assert l.count("inst-2") == 0
