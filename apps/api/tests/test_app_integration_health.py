"""Tests for App Integration Health — checks, status, availability."""

import pytest

from app.services.app_integration_health import AppIntegrationHealth


class TestRegister:
    def test_register(self):
        h = AppIntegrationHealth()
        h.register("inst-1", "stripe", "Stripe API")
        status = h.get_status("inst-1", "stripe")
        assert status.name == "Stripe API"

    def test_unregistered(self):
        h = AppIntegrationHealth()
        with pytest.raises(KeyError):
            h.record_check("inst-1", "nope", True)


class TestRecordCheck:
    def test_healthy(self):
        h = AppIntegrationHealth()
        h.register("inst-1", "stripe", "Stripe")
        c = h.record_check("inst-1", "stripe", True, latency_ms=50)
        assert c.healthy is True

    def test_unhealthy(self):
        h = AppIntegrationHealth()
        h.register("inst-1", "stripe", "Stripe")
        h.record_check("inst-1", "stripe", False, error="timeout")
        s = h.get_status("inst-1", "stripe")
        assert s.healthy is False
        assert s.last_error == "timeout"


class TestStatus:
    def test_availability(self):
        h = AppIntegrationHealth()
        h.register("inst-1", "stripe", "Stripe")
        for _ in range(8):
            h.record_check("inst-1", "stripe", True, latency_ms=50)
        for _ in range(2):
            h.record_check("inst-1", "stripe", False)
        s = h.get_status("inst-1", "stripe")
        assert s.availability_pct == 80.0
        assert s.check_count == 10

    def test_avg_latency(self):
        h = AppIntegrationHealth()
        h.register("inst-1", "stripe", "Stripe")
        h.record_check("inst-1", "stripe", True, latency_ms=100)
        h.record_check("inst-1", "stripe", True, latency_ms=200)
        s = h.get_status("inst-1", "stripe")
        assert s.avg_latency_ms == 150.0


class TestListIntegrations:
    def test_list(self):
        h = AppIntegrationHealth()
        h.register("inst-1", "stripe", "Stripe")
        h.register("inst-1", "sendgrid", "SendGrid")
        h.register("inst-2", "other", "Other")
        statuses = h.list_integrations("inst-1")
        assert len(statuses) == 2


class TestIsolation:
    def test_cross_installation(self):
        h = AppIntegrationHealth()
        h.register("inst-1", "stripe", "Stripe")
        with pytest.raises(KeyError):
            h.get_status("inst-2", "stripe")
