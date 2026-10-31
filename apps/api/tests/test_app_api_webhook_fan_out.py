import pytest
from app.services.app_api_webhook_fan_out import AppAPIWebhookFanOut

class TestFanOut:
    def test_fan_out(self):
        f = AppAPIWebhookFanOut()
        r = f.fan_out("inst-1", "push", ["https://a.com", "https://b.com", "https://c.com"])
        assert len(r.destinations) == 3

    def test_delivery(self):
        f = AppAPIWebhookFanOut()
        f.fan_out("inst-1", "push", ["https://a.com", "https://b.com"])
        f.record_delivery("inst-1", 0, True)
        f.record_delivery("inst-1", 0, False)
        r = f.recent("inst-1")[0]
        assert r.success_rate == 50.0

    def test_no_destinations(self):
        f = AppAPIWebhookFanOut()
        with pytest.raises(ValueError):
            f.fan_out("inst-1", "push", [])

    def test_isolation(self):
        f = AppAPIWebhookFanOut()
        f.fan_out("inst-1", "push", ["https://a.com"])
        assert f.total_fan_outs("inst-2") == 0
