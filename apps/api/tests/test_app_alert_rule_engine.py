"""Tests for App Alert Rule Engine — rules, evaluation, cooldown, resolution."""

import pytest

from app.services.app_alert_rule_engine import (
    AlertRule,
    AlertState,
    AppAlertRuleEngine,
    Operator,
)


class TestAddRule:
    def test_add(self):
        e = AppAlertRuleEngine()
        r = e.add_rule("inst-1", AlertRule(rule_id="r1", name="High CPU",
                                           metric="cpu_pct", operator=Operator.GT, threshold=90))
        assert r.rule_id == "r1"

    def test_duplicate(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="X", metric="x", operator=Operator.GT, threshold=0))
        with pytest.raises(ValueError, match="already exists"):
            e.add_rule("inst-1", AlertRule(rule_id="r1", name="Y", metric="y", operator=Operator.GT, threshold=0))


class TestEvaluate:
    def test_fires_on_threshold(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="High CPU",
                                       metric="cpu_pct", operator=Operator.GT, threshold=90))
        events = e.evaluate("inst-1", "cpu_pct", 95.0, now=1000.0)
        assert len(events) == 1
        assert events[0].state == AlertState.FIRING

    def test_no_fire_below_threshold(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="High CPU",
                                       metric="cpu_pct", operator=Operator.GT, threshold=90))
        events = e.evaluate("inst-1", "cpu_pct", 50.0)
        assert len(events) == 0

    def test_resolves(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="High CPU",
                                       metric="cpu_pct", operator=Operator.GT, threshold=90,
                                       cooldown_seconds=0))
        e.evaluate("inst-1", "cpu_pct", 95.0, now=1000.0)
        events = e.evaluate("inst-1", "cpu_pct", 50.0, now=1001.0)
        assert len(events) == 1
        assert events[0].state == AlertState.RESOLVED

    def test_lt_operator(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="Low Disk",
                                       metric="disk_free_gb", operator=Operator.LT, threshold=10))
        events = e.evaluate("inst-1", "disk_free_gb", 5.0, now=1000.0)
        assert len(events) == 1

    def test_unmatched_metric(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="X",
                                       metric="cpu_pct", operator=Operator.GT, threshold=90))
        events = e.evaluate("inst-1", "memory_pct", 99.0)
        assert len(events) == 0


class TestCooldown:
    def test_cooldown_prevents_refire(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="X",
                                       metric="x", operator=Operator.GT, threshold=50,
                                       cooldown_seconds=60))
        e.evaluate("inst-1", "x", 60, now=1000.0)  # fires
        # Resolve
        e.evaluate("inst-1", "x", 30, now=1001.0)
        # Try to fire again within cooldown
        events = e.evaluate("inst-1", "x", 60, now=1050.0)
        assert len(events) == 0  # cooldown active

    def test_fires_after_cooldown(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="X",
                                       metric="x", operator=Operator.GT, threshold=50,
                                       cooldown_seconds=60))
        e.evaluate("inst-1", "x", 60, now=1000.0)
        e.evaluate("inst-1", "x", 30, now=1001.0)  # resolve
        events = e.evaluate("inst-1", "x", 60, now=1061.0)
        assert len(events) == 1


class TestState:
    def test_initial_ok(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="X",
                                       metric="x", operator=Operator.GT, threshold=50))
        assert e.get_state("inst-1", "r1") == AlertState.OK

    def test_firing_state(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="X",
                                       metric="x", operator=Operator.GT, threshold=50))
        e.evaluate("inst-1", "x", 60, now=1000.0)
        assert e.get_state("inst-1", "r1") == AlertState.FIRING


class TestIsolation:
    def test_cross_installation(self):
        e = AppAlertRuleEngine()
        e.add_rule("inst-1", AlertRule(rule_id="r1", name="X",
                                       metric="x", operator=Operator.GT, threshold=50))
        events = e.evaluate("inst-2", "x", 60)
        assert len(events) == 0
