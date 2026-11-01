import pytest
from app.services.app_api_webhook_routing_rule import AppAPIWebhookRoutingRule

class TestRouting:
    def test_exact_match(self):
        r = AppAPIWebhookRoutingRule()
        r.add_rule("inst-1", "r1", "push", "https://a.com")
        assert r.route("inst-1", "push") == ["https://a.com"]

    def test_wildcard(self):
        r = AppAPIWebhookRoutingRule()
        r.add_rule("inst-1", "r1", "*", "https://catch-all.com")
        assert len(r.route("inst-1", "anything")) == 1

    def test_priority_order(self):
        r = AppAPIWebhookRoutingRule()
        r.add_rule("inst-1", "r1", "*", "https://low.com", priority=1)
        r.add_rule("inst-1", "r2", "*", "https://high.com", priority=10)
        dests = r.route("inst-1", "push")
        assert dests[0] == "https://high.com"

    def test_no_match(self):
        r = AppAPIWebhookRoutingRule()
        r.add_rule("inst-1", "r1", "push", "https://a.com")
        assert r.route("inst-1", "issue") == []

    def test_isolation(self):
        r = AppAPIWebhookRoutingRule()
        r.add_rule("inst-1", "r1", "*", "https://a.com")
        assert r.route("inst-2", "push") == []
