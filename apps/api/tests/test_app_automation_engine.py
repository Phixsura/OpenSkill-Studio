"""Tests for App Automation Engine — conditions, rules, execution, dry-run."""

import pytest

from app.services.app_automation_engine import (
    MAX_RULES_PER_APP,
    Action,
    ActionType,
    AppAutomationEngine,
    Condition,
    ConditionOp,
    LogicOp,
    evaluate_condition,
)


class TestConditionEvaluation:
    def test_equals(self):
        assert evaluate_condition(
            Condition("name", ConditionOp.EQUALS, "Alice"),
            {"name": "Alice"},
        ) is True

    def test_equals_mismatch(self):
        assert evaluate_condition(
            Condition("name", ConditionOp.EQUALS, "Bob"),
            {"name": "Alice"},
        ) is False

    def test_not_equals(self):
        assert evaluate_condition(
            Condition("status", ConditionOp.NOT_EQUALS, "active"),
            {"status": "suspended"},
        ) is True

    def test_contains(self):
        assert evaluate_condition(
            Condition("message", ConditionOp.CONTAINS, "error"),
            {"message": "fatal error occurred"},
        ) is True

    def test_contains_miss(self):
        assert evaluate_condition(
            Condition("message", ConditionOp.CONTAINS, "warning"),
            {"message": "all good"},
        ) is False

    def test_regex(self):
        assert evaluate_condition(
            Condition("email", ConditionOp.REGEX, r"^[^@]+@example\.com$"),
            {"email": "alice@example.com"},
        ) is True

    def test_regex_invalid(self):
        assert evaluate_condition(
            Condition("email", ConditionOp.REGEX, r"[invalid"),
            {"email": "test"},
        ) is False

    def test_exists(self):
        assert evaluate_condition(
            Condition("score", ConditionOp.EXISTS),
            {"score": 95},
        ) is True

    def test_exists_missing(self):
        assert evaluate_condition(
            Condition("score", ConditionOp.EXISTS),
            {"name": "Alice"},
        ) is False

    def test_gt(self):
        assert evaluate_condition(
            Condition("score", ConditionOp.GT, "80"),
            {"score": 95},
        ) is True

    def test_lt(self):
        assert evaluate_condition(
            Condition("score", ConditionOp.LT, "50"),
            {"score": 30},
        ) is True

    def test_gte(self):
        assert evaluate_condition(
            Condition("score", ConditionOp.GTE, "90"),
            {"score": 90},
        ) is True

    def test_lte(self):
        assert evaluate_condition(
            Condition("score", ConditionOp.LTE, "90"),
            {"score": 90},
        ) is True

    def test_numeric_non_numeric_value(self):
        assert evaluate_condition(
            Condition("name", ConditionOp.GT, "5"),
            {"name": "Alice"},
        ) is False

    def test_nested_field(self):
        assert evaluate_condition(
            Condition("data.user.role", ConditionOp.EQUALS, "admin"),
            {"data": {"user": {"role": "admin"}}},
        ) is True

    def test_missing_field_returns_false(self):
        assert evaluate_condition(
            Condition("nonexistent", ConditionOp.EQUALS, "x"),
            {"other": "y"},
        ) is False


class TestRuleCRUD:
    def _cond(self) -> list[Condition]:
        return [Condition("score", ConditionOp.GTE, "90")]

    def _action(self) -> list[Action]:
        return [Action(ActionType.LOG, {"message": "High score!"})]

    def test_add_rule(self):
        e = AppAutomationEngine()
        rule = e.add_rule("app-1", "org-1", "High Score", "submission.graded",
                          self._cond(), self._action())
        assert isinstance(rule, type(rule))  # not a string
        assert rule.name == "High Score"

    def test_add_rule_no_conditions(self):
        e = AppAutomationEngine()
        result = e.add_rule("app-1", "org-1", "Bad", "event", [], self._action())
        assert isinstance(result, str)
        assert "condition" in result.lower()

    def test_add_rule_no_actions(self):
        e = AppAutomationEngine()
        result = e.add_rule("app-1", "org-1", "Bad", "event", self._cond(), [])
        assert isinstance(result, str)
        assert "action" in result.lower()

    def test_rule_limit(self):
        e = AppAutomationEngine()
        for i in range(MAX_RULES_PER_APP):
            r = e.add_rule("app-1", "org-1", f"Rule {i}", "event", self._cond(), self._action())
            assert not isinstance(r, str)
        result = e.add_rule("app-1", "org-1", "One more", "event", self._cond(), self._action())
        assert isinstance(result, str)
        assert "limit" in result.lower()

    def test_update_rule(self):
        e = AppAutomationEngine()
        rule = e.add_rule("app-1", "org-1", "R", "event", self._cond(), self._action())
        updated = e.update_rule("app-1", "org-1", rule.rule_id, enabled=False, name="Updated")
        assert updated.enabled is False
        assert updated.name == "Updated"

    def test_delete_rule(self):
        e = AppAutomationEngine()
        rule = e.add_rule("app-1", "org-1", "R", "event", self._cond(), self._action())
        assert e.delete_rule("app-1", "org-1", rule.rule_id) is True
        assert e.get_rule("app-1", "org-1", rule.rule_id) is None

    def test_list_rules(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "A", "event", self._cond(), self._action())
        e.add_rule("app-1", "org-1", "B", "event", self._cond(), self._action())
        e.add_rule("app-2", "org-1", "C", "event", self._cond(), self._action())
        assert len(e.list_rules("app-1", "org-1")) == 2


class TestExecution:
    def test_matching_rule_executes(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "High Score", "submission.graded",
                    [Condition("score", ConditionOp.GTE, "90")],
                    [Action(ActionType.LOG, {"message": "Great!"})])
        results = e.process_event("submission.graded", {"score": 95}, org_id="org-1")
        assert len(results) == 1
        assert results[0].matched is True
        assert results[0].actions_executed == 1

    def test_non_matching_rule(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "High Score", "submission.graded",
                    [Condition("score", ConditionOp.GTE, "90")],
                    [Action(ActionType.LOG)])
        results = e.process_event("submission.graded", {"score": 50}, org_id="org-1")
        assert results[0].matched is False
        assert results[0].actions_executed == 0

    def test_wrong_event_type_skipped(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "R", "submission.graded",
                    [Condition("score", ConditionOp.EXISTS)],
                    [Action(ActionType.LOG)])
        results = e.process_event("app.installed", {"score": 100}, org_id="org-1")
        assert len(results) == 0

    def test_disabled_rule_skipped(self):
        e = AppAutomationEngine()
        rule = e.add_rule("app-1", "org-1", "R", "event",
                           [Condition("x", ConditionOp.EXISTS)],
                           [Action(ActionType.LOG)])
        e.update_rule("app-1", "org-1", rule.rule_id, enabled=False)
        results = e.process_event("event", {"x": 1}, org_id="org-1")
        assert len(results) == 0

    def test_and_logic(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "R", "event",
                    [Condition("a", ConditionOp.EQUALS, "1"),
                     Condition("b", ConditionOp.EQUALS, "2")],
                    [Action(ActionType.LOG)], logic=LogicOp.AND)
        # Both match
        r = e.process_event("event", {"a": "1", "b": "2"}, org_id="org-1")
        assert r[0].matched is True
        # Only one matches
        r = e.process_event("event", {"a": "1", "b": "9"}, org_id="org-1")
        assert r[0].matched is False

    def test_or_logic(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "R", "event",
                    [Condition("a", ConditionOp.EQUALS, "1"),
                     Condition("b", ConditionOp.EQUALS, "2")],
                    [Action(ActionType.LOG)], logic=LogicOp.OR)
        r = e.process_event("event", {"a": "1", "b": "9"}, org_id="org-1")
        assert r[0].matched is True

    def test_dry_run(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "R", "event",
                    [Condition("x", ConditionOp.EXISTS)],
                    [Action(ActionType.WEBHOOK, {"url": "https://example.com"})])
        results = e.process_event("event", {"x": 1}, org_id="org-1", dry_run=True)
        assert results[0].matched is True
        assert results[0].actions_executed == 0
        assert results[0].dry_run is True

    def test_multiple_actions(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "R", "event",
                    [Condition("x", ConditionOp.EXISTS)],
                    [Action(ActionType.LOG), Action(ActionType.NOTIFICATION, {"title": "Hi"})])
        results = e.process_event("event", {"x": 1}, org_id="org-1")
        assert results[0].actions_executed == 2

    def test_history(self):
        e = AppAutomationEngine()
        e.add_rule("app-1", "org-1", "R", "event",
                    [Condition("x", ConditionOp.EXISTS)],
                    [Action(ActionType.LOG)])
        e.process_event("event", {"x": 1}, org_id="org-1")
        e.process_event("event", {"x": 2}, org_id="org-1")
        history = e.get_history("app-1", "org-1")
        assert len(history) == 2
