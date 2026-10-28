"""Tests for App Metric Alert — rules, evaluate, firing state."""

import pytest

from app.services.app_metric_alert import AppMetricAlert, AlertState


class TestAddRule:
    def test_add(self):
        a = AppMetricAlert()
        r = a.add_rule("inst-1", "r1", "cpu_pct", "gt", 80.0, "critical")
        assert r.state == AlertState.OK

    def test_invalid_operator(self):
        a = AppMetricAlert()
        with pytest.raises(ValueError):
            a.add_rule("inst-1", "r1", "cpu", "bad", 50)


class TestEvaluate:
    def test_fires(self):
        a = AppMetricAlert()
        a.add_rule("inst-1", "r1", "cpu_pct", "gt", 80.0)
        firing = a.evaluate("inst-1", "cpu_pct", 95.0)
        assert len(firing) == 1
        assert firing[0].state == AlertState.FIRING

    def test_ok(self):
        a = AppMetricAlert()
        a.add_rule("inst-1", "r1", "cpu_pct", "gt", 80.0)
        firing = a.evaluate("inst-1", "cpu_pct", 50.0)
        assert firing == []

    def test_resolves(self):
        a = AppMetricAlert()
        a.add_rule("inst-1", "r1", "cpu_pct", "gt", 80.0)
        a.evaluate("inst-1", "cpu_pct", 95.0)  # fire
        a.evaluate("inst-1", "cpu_pct", 50.0)  # resolve
        rules = a.list_rules("inst-1")
        assert rules[0].state == AlertState.RESOLVED

    def test_fire_count(self):
        a = AppMetricAlert()
        a.add_rule("inst-1", "r1", "cpu_pct", "gt", 80.0)
        a.evaluate("inst-1", "cpu_pct", 95.0)
        a.evaluate("inst-1", "cpu_pct", 50.0)  # resolve
        a.evaluate("inst-1", "cpu_pct", 90.0)  # fire again
        assert a.list_rules("inst-1")[0].fire_count == 2


class TestIsolation:
    def test_cross(self):
        a = AppMetricAlert()
        a.add_rule("inst-1", "r1", "cpu_pct", "gt", 80.0)
        assert a.list_rules("inst-2") == []
