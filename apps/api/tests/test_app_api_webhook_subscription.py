"""Tests for App API Webhook Subscription — subscribe, match, wildcard."""

import pytest
from app.services.app_api_webhook_subscription import AppAPIWebhookSubscription


class TestSubscribe:
    def test_subscribe(self):
        s = AppAPIWebhookSubscription()
        sub = s.subscribe("inst-1", "s1", "https://a.com", "push")
        assert sub.enabled is True

    def test_duplicate(self):
        s = AppAPIWebhookSubscription()
        s.subscribe("inst-1", "s1", "https://a.com", "push")
        with pytest.raises(ValueError):
            s.subscribe("inst-1", "s1", "https://b.com", "issue")


class TestMatch:
    def test_exact(self):
        s = AppAPIWebhookSubscription()
        s.subscribe("inst-1", "s1", "https://a.com", "push")
        assert len(s.matches("inst-1", "push")) == 1
        assert len(s.matches("inst-1", "issue")) == 0

    def test_wildcard(self):
        s = AppAPIWebhookSubscription()
        s.subscribe("inst-1", "s1", "https://a.com", "*")
        assert len(s.matches("inst-1", "anything")) == 1

    def test_prefix_wildcard(self):
        s = AppAPIWebhookSubscription()
        s.subscribe("inst-1", "s1", "https://a.com", "issue.*")
        assert len(s.matches("inst-1", "issue.created")) == 1
        assert len(s.matches("inst-1", "push")) == 0

    def test_disabled_skipped(self):
        s = AppAPIWebhookSubscription()
        s.subscribe("inst-1", "s1", "https://a.com", "*")
        s.toggle("inst-1", "s1", False)
        assert len(s.matches("inst-1", "push")) == 0


class TestIsolation:
    def test_cross(self):
        s = AppAPIWebhookSubscription()
        s.subscribe("inst-1", "s1", "https://a.com", "*")
        assert s.matches("inst-2", "push") == []
