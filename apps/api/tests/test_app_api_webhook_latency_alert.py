import pytest
from app.services.app_api_webhook_latency_alert import AppAPIWebhookLatencyAlert

class TestLatencyAlert:
    def test_set(self):
        a = AppAPIWebhookLatencyAlert()
        alert = a.set_alert("inst-1", "a1", "https://a.com", 500)
        assert alert.triggered is False

    def test_trigger(self):
        a = AppAPIWebhookLatencyAlert()
        a.set_alert("inst-1", "a1", "https://a.com", 500)
        a.evaluate("inst-1", "a1", 800)
        assert len(a.triggered_alerts("inst-1")) == 1

    def test_resolve(self):
        a = AppAPIWebhookLatencyAlert()
        a.set_alert("inst-1", "a1", "https://a.com", 500)
        a.evaluate("inst-1", "a1", 800)
        a.evaluate("inst-1", "a1", 200)
        assert a.triggered_alerts("inst-1") == []

    def test_isolation(self):
        a = AppAPIWebhookLatencyAlert()
        a.set_alert("inst-1", "a1", "https://a.com", 500)
        assert a.list_alerts("inst-2") == []
