"""Tests for App API Usage Alert — rules, evaluate, fire."""

import pytest
from app.services.app_api_usage_alert import AppAPIUsageAlert


class TestAdd:
    def test_add(self):
        a = AppAPIUsageAlert()
        r = a.add_rule("inst-1", "r1", "api_calls", "exceeds", 10000)
        assert r.fired is False

    def test_invalid_condition(self):
        a = AppAPIUsageAlert()
        with pytest.raises(ValueError):
            a.add_rule("inst-1", "r1", "api_calls", "bogus", 100)


class TestEvaluate:
    def test_exceeds(self):
        a = AppAPIUsageAlert()
        a.add_rule("inst-1", "r1", "api_calls", "exceeds", 1000)
        fired = a.evaluate("inst-1", "api_calls", 1500, 800)
        assert len(fired) == 1

    def test_spike(self):
        a = AppAPIUsageAlert()
        a.add_rule("inst-1", "r1", "api_calls", "spike", 50)  # 50% increase
        fired = a.evaluate("inst-1", "api_calls", 200, 100)  # 100% increase
        assert len(fired) == 1

    def test_drop(self):
        a = AppAPIUsageAlert()
        a.add_rule("inst-1", "r1", "api_calls", "drop", 50)
        fired = a.evaluate("inst-1", "api_calls", 30, 100)  # 70% drop
        assert len(fired) == 1

    def test_no_fire(self):
        a = AppAPIUsageAlert()
        a.add_rule("inst-1", "r1", "api_calls", "exceeds", 1000)
        fired = a.evaluate("inst-1", "api_calls", 500, 400)
        assert fired == []


class TestIsolation:
    def test_cross(self):
        a = AppAPIUsageAlert()
        a.add_rule("inst-1", "r1", "api_calls", "exceeds", 100)
        assert a.list_rules("inst-2") == []
