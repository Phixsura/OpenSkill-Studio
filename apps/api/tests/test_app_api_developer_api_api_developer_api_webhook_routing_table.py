import pytest
from app.services.app_api_developer_api_api_developer_api_webhook_routing_table import AppAPIDeveloperAPIApiDeveloperApiWebhookRoutingTable

class TestRoutingTable:
    def test_add_rule(self):
        t = AppAPIDeveloperAPIApiDeveloperApiWebhookRoutingTable()
        r = t.add_rule("inst-1", "r1", "order.*", "https://billing.com/hook")
        assert r.event_pattern == "order.*"

    def test_https_required(self):
        t = AppAPIDeveloperAPIApiDeveloperApiWebhookRoutingTable()
        with pytest.raises(ValueError):
            t.add_rule("inst-1", "r1", "order.*", "http://bad.com")

    def test_route_match(self):
        t = AppAPIDeveloperAPIApiDeveloperApiWebhookRoutingTable()
        t.add_rule("inst-1", "r1", "order.*", "https://a.com")
        t.add_rule("inst-1", "r2", "user.*", "https://b.com")
        matched = t.route("inst-1", "order.created")
        assert len(matched) == 1
        assert matched[0].destination == "https://a.com"

    def test_disabled_skipped(self):
        t = AppAPIDeveloperAPIApiDeveloperApiWebhookRoutingTable()
        t.add_rule("inst-1", "r1", "*", "https://a.com")
        t.toggle("inst-1", "r1", False)
        assert len(t.route("inst-1", "anything")) == 0

    def test_match_count(self):
        t = AppAPIDeveloperAPIApiDeveloperApiWebhookRoutingTable()
        t.add_rule("inst-1", "r1", "push", "https://a.com")
        t.route("inst-1", "push")
        t.route("inst-1", "push")
        assert t.top_rules("inst-1")[0].matches == 2

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiWebhookRoutingTable()
        t.add_rule("inst-1", "r1", "*", "https://a.com")
        assert len(t.all_rules("inst-2")) == 0
