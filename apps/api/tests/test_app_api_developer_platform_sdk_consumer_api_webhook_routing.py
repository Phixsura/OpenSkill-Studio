"""Tests for Consumer API Webhook Routing service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_routing import (
    WebhookRouter, RoutingRule,
)


class TestWebhookRouter:
    def test_route_eq(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "Orders", "event", "eq", "order.created", "https://orders.com/hook"))
        result = svc.route({"event": "order.created", "data": {}})
        assert result["routed"] is True
        assert result["target_url"] == "https://orders.com/hook"

    def test_route_no_match(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "Orders", "event", "eq", "order.created", "https://orders.com/hook"))
        result = svc.route({"event": "user.created"})
        assert result["routed"] is False

    def test_default_fallback(self):
        svc = WebhookRouter()
        svc.set_default("https://default.com/hook")
        result = svc.route({"event": "unknown"})
        assert result["routed"] is True
        assert result["default"] is True

    def test_contains(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "Errors", "message", "contains", "error", "https://err.com"))
        result = svc.route({"message": "An error occurred"})
        assert result["routed"] is True

    def test_gt(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "High Value", "amount", "gt", "100", "https://high.com"))
        assert svc.route({"amount": 150})["routed"] is True
        assert svc.route({"amount": 50})["routed"] is False

    def test_nested_field(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "VIP", "user.tier", "eq", "vip", "https://vip.com"))
        result = svc.route({"user": {"tier": "vip", "id": 1}})
        assert result["routed"] is True

    def test_exists(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "Has Error", "error", "exists", "", "https://err.com"))
        assert svc.route({"error": "timeout"})["routed"] is True
        assert svc.route({"data": "ok"})["routed"] is False

    def test_regex(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "UUID", "id", "regex", r"^[0-9a-f]{8}-", "https://uuid.com"))
        assert svc.route({"id": "a1b2c3d4-5678"})["routed"] is True

    def test_priority(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "Low", "event", "eq", "test", "https://low.com", priority=1))
        svc.add_rule(RoutingRule("r2", "High", "event", "eq", "test", "https://high.com", priority=10))
        result = svc.route({"event": "test"})
        assert result["target_url"] == "https://high.com"

    def test_remove_rule(self):
        svc = WebhookRouter()
        svc.add_rule(RoutingRule("r1", "X", "event", "eq", "test", "https://x.com"))
        svc.remove_rule("r1")
        assert svc.list_rules() == []

    def test_invalid_operator(self):
        svc = WebhookRouter()
        with pytest.raises(ValueError):
            svc.add_rule(RoutingRule("r1", "X", "event", "like", "test", "https://x.com"))

    def test_isolation(self):
        a, b = WebhookRouter(), WebhookRouter()
        a.add_rule(RoutingRule("r1", "X", "event", "eq", "test", "https://x.com"))
        assert b.route({"event": "test"})["routed"] is False
