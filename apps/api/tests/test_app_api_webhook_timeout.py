"""Tests for App API Webhook Timeout — configure, defaults, frequent."""

import pytest
from app.services.app_api_webhook_timeout import AppAPIWebhookTimeout


class TestConfigure:
    def test_configure(self):
        t = AppAPIWebhookTimeout()
        c = t.configure("inst-1", "https://a.com", 3000, 10000)
        assert c.connect_timeout_ms == 3000

    def test_min_timeout(self):
        t = AppAPIWebhookTimeout()
        with pytest.raises(ValueError):
            t.configure("inst-1", "https://a.com", 50)


class TestDefaults:
    def test_default(self):
        t = AppAPIWebhookTimeout(default_connect=2000, default_read=15000)
        c = t.get_timeout("inst-1", "https://unconfigured.com")
        assert c.connect_timeout_ms == 2000
        assert c.read_timeout_ms == 15000


class TestFrequent:
    def test_frequent(self):
        t = AppAPIWebhookTimeout()
        for _ in range(5):
            t.record_timeout("inst-1", "https://slow.com")
        assert len(t.frequent_timeouts("inst-1", threshold=5)) == 1

    def test_below_threshold(self):
        t = AppAPIWebhookTimeout()
        t.record_timeout("inst-1", "https://a.com")
        assert t.frequent_timeouts("inst-1") == []


class TestIsolation:
    def test_cross(self):
        t = AppAPIWebhookTimeout()
        t.configure("inst-1", "https://a.com")
        assert t.list_configs("inst-2") == []
