from app.services.app_marketplace_extension_automation_rules import (
    AutomationRuleService, LogicOp,
)


def test_create_and_evaluate():
    svc = AutomationRuleService()
    svc.create_rule("ext-1", "Auto-notify on deploy", "deploy",
                    [{"field": "status", "operator": "equals", "value": "success"}],
                    [{"type": "send_notification", "params": {"channel": "slack"}}])
    results = svc.evaluate("ext-1", "deploy", {"status": "success"})
    assert len(results) == 1
    assert results[0].matched is True
    assert "send_notification" in results[0].actions_executed


def test_condition_not_met():
    svc = AutomationRuleService()
    svc.create_rule("ext-1", "Rule", "deploy",
                    [{"field": "status", "operator": "equals", "value": "success"}],
                    [{"type": "notify"}])
    results = svc.evaluate("ext-1", "deploy", {"status": "failed"})
    assert results[0].matched is False
    assert results[0].actions_executed == []


def test_or_logic():
    svc = AutomationRuleService()
    svc.create_rule("ext-1", "Alert on error or warning", "log",
                    [{"field": "level", "operator": "equals", "value": "error"},
                     {"field": "level", "operator": "equals", "value": "warning"}],
                    [{"type": "alert"}], logic=LogicOp.OR)
    results = svc.evaluate("ext-1", "log", {"level": "warning"})
    assert results[0].matched is True


def test_dry_run():
    svc = AutomationRuleService()
    rule = svc.create_rule("ext-1", "Rule", "deploy",
                           [{"field": "env", "operator": "equals", "value": "prod"}],
                           [{"type": "scale_up"}])
    results = svc.evaluate("ext-1", "deploy", {"env": "prod"}, dry_run=True)
    assert results[0].matched is True
    assert results[0].actions_executed == []
    assert rule.execution_count == 0


def test_greater_than():
    svc = AutomationRuleService()
    svc.create_rule("ext-1", "High CPU alert", "metrics",
                    [{"field": "cpu", "operator": "greater_than", "value": "80"}],
                    [{"type": "alert"}])
    r1 = svc.evaluate("ext-1", "metrics", {"cpu": 95})
    assert r1[0].matched is True
    r2 = svc.evaluate("ext-1", "metrics", {"cpu": 50})
    assert r2[0].matched is False


def test_exists_operator():
    svc = AutomationRuleService()
    svc.create_rule("ext-1", "Has error", "event",
                    [{"field": "error", "operator": "exists"}],
                    [{"type": "log_error"}])
    r1 = svc.evaluate("ext-1", "event", {"error": "something broke"})
    assert r1[0].matched is True
    r2 = svc.evaluate("ext-1", "event", {"status": "ok"})
    assert r2[0].matched is False


def test_toggle_rule():
    svc = AutomationRuleService()
    rule = svc.create_rule("ext-1", "Rule", "e", [], [{"type": "a"}])
    svc.toggle(rule.rule_id)
    assert rule.enabled is False
    results = svc.evaluate("ext-1", "e", {})
    assert len(results) == 0
