"""App health alert tests."""
import pytest
from app.services.app_health_alerts import evaluate_rule, check_health_alerts, AlertRule, DEFAULT_RULES

def test_rule_triggered():
    rule = AlertRule("test", "error_rate_pct", "gte", 10.0, "warning")
    alert = evaluate_rule(rule, {"error_rate_pct": 15.0})
    assert alert is not None
    assert alert["severity"] == "warning"

def test_rule_not_triggered():
    rule = AlertRule("test", "error_rate_pct", "gte", 10.0, "warning")
    assert evaluate_rule(rule, {"error_rate_pct": 5.0}) is None

def test_rule_missing_metric():
    rule = AlertRule("test", "missing", "gte", 10.0, "info")
    assert evaluate_rule(rule, {}) is None

def test_check_healthy():
    alerts = check_health_alerts({"score": 100, "error_rate_pct": 0.0})
    assert len(alerts) == 0

def test_check_degraded():
    alerts = check_health_alerts({"score": 70, "error_rate_pct": 15.0})
    assert len(alerts) > 0
    severities = {a["severity"] for a in alerts}
    assert "warning" in severities

def test_check_critical():
    alerts = check_health_alerts({"score": 30, "error_rate_pct": 30.0})
    assert any(a["severity"] == "critical" for a in alerts)

def test_custom_rules():
    rules = [AlertRule("custom", "latency_ms", "gt", 1000, "warning")]
    alerts = check_health_alerts({"latency_ms": 1500}, rules=rules)
    assert len(alerts) == 1
    assert alerts[0]["rule"] == "custom"

def test_default_rules_count():
    assert len(DEFAULT_RULES) >= 4
