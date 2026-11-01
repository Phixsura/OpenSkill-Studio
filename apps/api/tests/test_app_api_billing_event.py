"""Tests for App API Billing Event — record, total, by_type."""

import pytest
from app.services.app_api_billing_event import AppAPIBillingEvent


class TestRecord:
    def test_record(self):
        b = AppAPIBillingEvent()
        e = b.record("inst-1", "e1", "api_call", 0.001, period="2024-01")
        assert e.amount == 0.001

    def test_negative(self):
        b = AppAPIBillingEvent()
        with pytest.raises(ValueError):
            b.record("inst-1", "e1", "api_call", -1)


class TestAggregate:
    def test_total(self):
        b = AppAPIBillingEvent()
        b.record("inst-1", "e1", "api_call", 10.0, period="2024-01")
        b.record("inst-1", "e2", "storage", 5.0, period="2024-01")
        assert b.total("inst-1", "2024-01") == 15.0

    def test_by_type(self):
        b = AppAPIBillingEvent()
        b.record("inst-1", "e1", "api_call", 10.0)
        b.record("inst-1", "e2", "api_call", 5.0)
        b.record("inst-1", "e3", "storage", 3.0)
        types = b.by_type("inst-1")
        assert types["api_call"] == 15.0
        assert types["storage"] == 3.0


class TestIsolation:
    def test_cross(self):
        b = AppAPIBillingEvent()
        b.record("inst-1", "e1", "api_call", 10.0)
        assert b.count("inst-2") == 0
