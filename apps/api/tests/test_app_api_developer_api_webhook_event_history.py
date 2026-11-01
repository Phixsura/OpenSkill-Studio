import pytest
from app.services.app_api_developer_api_webhook_event_history import AppAPIDeveloperAPIWebhookEventHistory

class TestHistory:
    def test_record(self):
        h = AppAPIDeveloperAPIWebhookEventHistory()
        e = h.record("inst-1", "e1", "push", "https://a.com", "delivered", 50)
        assert e.status == "delivered"

    def test_invalid_status(self):
        h = AppAPIDeveloperAPIWebhookEventHistory()
        with pytest.raises(ValueError):
            h.record("inst-1", "e1", "push", "https://a.com", "unknown", 50)

    def test_by_status(self):
        h = AppAPIDeveloperAPIWebhookEventHistory()
        h.record("inst-1", "e1", "push", "https://a.com", "delivered", 50)
        h.record("inst-1", "e2", "push", "https://a.com", "failed", 100)
        assert len(h.by_status("inst-1", "failed")) == 1

    def test_isolation(self):
        h = AppAPIDeveloperAPIWebhookEventHistory()
        h.record("inst-1", "e1", "push", "https://a.com", "delivered", 50)
        assert h.count("inst-2") == 0
