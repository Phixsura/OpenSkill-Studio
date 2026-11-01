"""Tests for App API Webhook IP Filter — allow, block, check."""

import pytest
from app.services.app_api_webhook_ip_filter import AppAPIWebhookIPFilter


class TestRules:
    def test_add(self):
        f = AppAPIWebhookIPFilter()
        r = f.add_rule("inst-1", "r1", "10.0.0.0/8", "block")
        assert r.action == "block"

    def test_invalid_cidr(self):
        f = AppAPIWebhookIPFilter()
        with pytest.raises(ValueError):
            f.add_rule("inst-1", "r1", "bad", "allow")


class TestCheck:
    def test_blocked(self):
        f = AppAPIWebhookIPFilter()
        f.add_rule("inst-1", "r1", "10.0.0.0/8", "block")
        assert f.check("inst-1", "10.0.0.5") is False
        assert f.blocked_count("inst-1") == 1

    def test_allowed(self):
        f = AppAPIWebhookIPFilter()
        f.add_rule("inst-1", "r1", "10.0.0.0/8", "block")
        assert f.check("inst-1", "192.168.1.1") is True

    def test_no_rules_allows(self):
        f = AppAPIWebhookIPFilter()
        assert f.check("inst-1", "1.2.3.4") is True


class TestIsolation:
    def test_cross(self):
        f = AppAPIWebhookIPFilter()
        f.add_rule("inst-1", "r1", "10.0.0.0/8", "block")
        assert f.check("inst-2", "10.0.0.1") is True
