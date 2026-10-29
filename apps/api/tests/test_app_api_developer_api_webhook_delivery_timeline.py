import pytest
from app.services.app_api_developer_api_webhook_delivery_timeline import AppAPIDeveloperAPIWebhookDeliveryTimeline

class TestTimeline:
    def test_record(self):
        t = AppAPIDeveloperAPIWebhookDeliveryTimeline()
        e = t.record("inst-1", "d1", "push", "https://a.com", "success", 50)
        assert e.status == "success"

    def test_invalid_status(self):
        t = AppAPIDeveloperAPIWebhookDeliveryTimeline()
        with pytest.raises(ValueError):
            t.record("inst-1", "d1", "push", "https://a.com", "unknown", 50)

    def test_failures(self):
        t = AppAPIDeveloperAPIWebhookDeliveryTimeline()
        t.record("inst-1", "d1", "push", "https://a.com", "success", 50)
        t.record("inst-1", "d2", "push", "https://a.com", "failure", 100)
        t.record("inst-1", "d3", "push", "https://a.com", "timeout", 5000)
        assert len(t.failures("inst-1")) == 2

    def test_isolation(self):
        t = AppAPIDeveloperAPIWebhookDeliveryTimeline()
        t.record("inst-1", "d1", "push", "https://a.com", "success", 50)
        assert t.count("inst-2") == 0
