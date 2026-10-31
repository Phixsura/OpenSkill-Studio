import pytest
from app.services.app_api_webhook_digest_subscription import AppAPIWebhookDigestSubscription

class TestDigest:
    def test_subscribe(self):
        d = AppAPIWebhookDigestSubscription()
        s = d.subscribe("inst-1", "s1", "https://a.com", "daily", ["push"])
        assert s.frequency == "daily"

    def test_invalid_freq(self):
        d = AppAPIWebhookDigestSubscription()
        with pytest.raises(ValueError):
            d.subscribe("inst-1", "s1", "https://a.com", "monthly")

    def test_toggle(self):
        d = AppAPIWebhookDigestSubscription()
        d.subscribe("inst-1", "s1", "https://a.com", "hourly")
        d.toggle("inst-1", "s1", False)
        assert d.active_subscriptions("inst-1") == []

    def test_digest_count(self):
        d = AppAPIWebhookDigestSubscription()
        d.subscribe("inst-1", "s1", "https://a.com", "daily")
        d.record_digest("inst-1", "s1")
        assert d.list_subscriptions("inst-1")[0].digest_count == 1

    def test_isolation(self):
        d = AppAPIWebhookDigestSubscription()
        d.subscribe("inst-1", "s1", "https://a.com", "daily")
        assert d.list_subscriptions("inst-2") == []
