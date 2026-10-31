"""Tests for App Webhook Endpoint — register, delivery, event matching."""

import pytest

from app.services.app_webhook_endpoint import AppWebhookEndpoint


class TestRegister:
    def test_register(self):
        w = AppWebhookEndpoint()
        ep = w.register("inst-1", "ep1", "https://hooks.example.com", ["push", "issue"])
        assert ep.events == ["push", "issue"]

    def test_no_events(self):
        w = AppWebhookEndpoint()
        with pytest.raises(ValueError):
            w.register("inst-1", "ep1", "https://hooks.example.com", [])


class TestDelivery:
    def test_success_rate(self):
        w = AppWebhookEndpoint()
        w.register("inst-1", "ep1", "https://hooks.example.com", ["push"])
        for _ in range(9):
            w.record_delivery("inst-1", "ep1", True)
        w.record_delivery("inst-1", "ep1", False)
        ep = w.list_endpoints("inst-1")[0]
        assert ep.success_rate == 90.0


class TestEventMatch:
    def test_match(self):
        w = AppWebhookEndpoint()
        w.register("inst-1", "ep1", "https://a.com", ["push"])
        w.register("inst-1", "ep2", "https://b.com", ["issue"])
        eps = w.endpoints_for_event("inst-1", "push")
        assert len(eps) == 1
        assert eps[0].endpoint_id == "ep1"

    def test_disabled_skipped(self):
        w = AppWebhookEndpoint()
        w.register("inst-1", "ep1", "https://a.com", ["push"])
        w.toggle("inst-1", "ep1", False)
        assert w.endpoints_for_event("inst-1", "push") == []


class TestIsolation:
    def test_cross(self):
        w = AppWebhookEndpoint()
        w.register("inst-1", "ep1", "https://a.com", ["push"])
        assert w.list_endpoints("inst-2") == []
