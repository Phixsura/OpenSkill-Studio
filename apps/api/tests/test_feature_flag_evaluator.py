"""Tests for Feature Flag Evaluator — boolean, percentage, user-list, dependencies."""

import pytest

from app.services.feature_flag_evaluator import (
    EvalContext,
    FeatureFlag,
    FeatureFlagEvaluator,
    FlagRule,
    FlagStatus,
    FlagType,
    _deterministic_bucket,
)


class TestDeterministicBucket:
    def test_stable(self):
        b1 = _deterministic_bucket("flag-a", "user-1")
        b2 = _deterministic_bucket("flag-a", "user-1")
        assert b1 == b2

    def test_range_0_99(self):
        for i in range(100):
            b = _deterministic_bucket("flag-x", f"user-{i}")
            assert 0 <= b <= 99

    def test_different_flags_different_buckets(self):
        buckets = {_deterministic_bucket(f"flag-{i}", "user-1") for i in range(20)}
        assert len(buckets) > 1  # not all the same


class TestBooleanFlags:
    def test_simple_boolean_on(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="new-ui", description="New UI", default_value=False,
            rules=[FlagRule(FlagType.BOOLEAN, True)],
        ))
        result = ev.evaluate("new-ui", EvalContext(user_id="u1"))
        assert result.enabled is True
        assert result.reason == "rule_0"

    def test_simple_boolean_off(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="new-ui", description="New UI", default_value=True,
            rules=[FlagRule(FlagType.BOOLEAN, False)],
        ))
        assert ev.is_enabled("new-ui", EvalContext(user_id="u1")) is False

    def test_default_when_no_rules(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="feat-x", description="X", default_value=True))
        result = ev.evaluate("feat-x", EvalContext())
        assert result.enabled is True
        assert result.reason == "default"

    def test_unknown_flag_returns_false(self):
        ev = FeatureFlagEvaluator()
        result = ev.evaluate("nonexistent", EvalContext())
        assert result.enabled is False
        assert result.reason == "flag_not_found"


class TestPercentageRollout:
    def test_0_percent_always_off(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="rollout", description="Rollout",
            rules=[FlagRule(FlagType.PERCENTAGE, 0)],
        ))
        for i in range(50):
            assert ev.is_enabled("rollout", EvalContext(user_id=f"user-{i}")) is False

    def test_100_percent_always_on(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="rollout", description="Rollout",
            rules=[FlagRule(FlagType.PERCENTAGE, 100)],
        ))
        for i in range(50):
            assert ev.is_enabled("rollout", EvalContext(user_id=f"user-{i}")) is True

    def test_50_percent_splits(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="rollout", description="Rollout",
            rules=[FlagRule(FlagType.PERCENTAGE, 50)],
        ))
        results = [ev.is_enabled("rollout", EvalContext(user_id=f"user-{i}"))
                    for i in range(200)]
        on_count = sum(results)
        # Should be roughly 50% (within statistical tolerance)
        assert 60 < on_count < 140

    def test_sticky_for_same_user(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="rollout", description="Rollout",
            rules=[FlagRule(FlagType.PERCENTAGE, 50)],
        ))
        r1 = ev.is_enabled("rollout", EvalContext(user_id="sticky-user"))
        r2 = ev.is_enabled("rollout", EvalContext(user_id="sticky-user"))
        assert r1 == r2  # same user → same result


class TestUserListTargeting:
    def test_user_in_list(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="beta", description="Beta",
            rules=[FlagRule(FlagType.USER_LIST, ["u1", "u2", "u3"])],
        ))
        assert ev.is_enabled("beta", EvalContext(user_id="u2")) is True

    def test_user_not_in_list(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="beta", description="Beta", default_value=False,
            rules=[FlagRule(FlagType.USER_LIST, ["u1", "u2"])],
        ))
        assert ev.is_enabled("beta", EvalContext(user_id="u99")) is False

    def test_no_user_id_skips_rule(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="beta", description="Beta", default_value=False,
            rules=[FlagRule(FlagType.USER_LIST, ["u1"])],
        ))
        result = ev.evaluate("beta", EvalContext())
        assert result.enabled is False
        assert result.reason == "default"


class TestTenantListTargeting:
    def test_tenant_in_list(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="enterprise", description="Enterprise",
            rules=[FlagRule(FlagType.TENANT_LIST, ["org-a", "org-b"])],
        ))
        assert ev.is_enabled("enterprise", EvalContext(tenant_id="org-a")) is True

    def test_tenant_not_in_list(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="enterprise", description="Enterprise", default_value=False,
            rules=[FlagRule(FlagType.TENANT_LIST, ["org-a"])],
        ))
        assert ev.is_enabled("enterprise", EvalContext(tenant_id="org-z")) is False


class TestTenantOverrides:
    def test_override_enables(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="feat", description="F", default_value=False))
        ev.set_override("feat", "org-1", True)
        assert ev.is_enabled("feat", EvalContext(tenant_id="org-1")) is True

    def test_override_disables(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(
            key="feat", description="F",
            rules=[FlagRule(FlagType.BOOLEAN, True)],
        ))
        ev.set_override("feat", "org-1", False)
        assert ev.is_enabled("feat", EvalContext(tenant_id="org-1")) is False

    def test_remove_override(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="feat", description="F", default_value=False))
        ev.set_override("feat", "org-1", True)
        ev.remove_override("feat", "org-1")
        assert ev.is_enabled("feat", EvalContext(tenant_id="org-1")) is False


class TestDependencies:
    def test_dependency_met(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="base", description="Base",
                                rules=[FlagRule(FlagType.BOOLEAN, True)]))
        ev.register(FeatureFlag(key="advanced", description="Adv",
                                depends_on=["base"],
                                rules=[FlagRule(FlagType.BOOLEAN, True)]))
        assert ev.is_enabled("advanced", EvalContext(user_id="u1")) is True

    def test_dependency_not_met(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="base", description="Base",
                                rules=[FlagRule(FlagType.BOOLEAN, False)]))
        ev.register(FeatureFlag(key="advanced", description="Adv",
                                depends_on=["base"],
                                rules=[FlagRule(FlagType.BOOLEAN, True)]))
        result = ev.evaluate("advanced", EvalContext(user_id="u1"))
        assert result.enabled is False
        assert "dependency_not_met" in result.reason


class TestFlagStatus:
    def test_disabled_returns_default(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="feat", description="F", status=FlagStatus.DISABLED,
                                default_value=True,
                                rules=[FlagRule(FlagType.BOOLEAN, False)]))
        result = ev.evaluate("feat", EvalContext())
        assert result.enabled is True
        assert "disabled" in result.reason

    def test_archived_returns_default(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="feat", description="F", status=FlagStatus.ARCHIVED,
                                default_value=False))
        result = ev.evaluate("feat", EvalContext())
        assert result.enabled is False


class TestBulkAndListing:
    def test_evaluate_bulk(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="a", description="A",
                                rules=[FlagRule(FlagType.BOOLEAN, True)]))
        ev.register(FeatureFlag(key="b", description="B",
                                rules=[FlagRule(FlagType.BOOLEAN, False)]))
        results = ev.evaluate_bulk(["a", "b", "unknown"], EvalContext())
        assert results == {"a": True, "b": False, "unknown": False}

    def test_list_flags(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="z", description="Z"))
        ev.register(FeatureFlag(key="a", description="A"))
        flags = ev.list_flags()
        assert [f.key for f in flags] == ["a", "z"]

    def test_list_by_status(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="a", description="A", status=FlagStatus.ACTIVE))
        ev.register(FeatureFlag(key="b", description="B", status=FlagStatus.DISABLED))
        active = ev.list_flags(FlagStatus.ACTIVE)
        assert len(active) == 1
        assert active[0].key == "a"


class TestAuditLog:
    def test_eval_log(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="f", description="F",
                                rules=[FlagRule(FlagType.BOOLEAN, True)]))
        ev.evaluate("f", EvalContext())
        ev.evaluate("f", EvalContext())
        log_entries = ev.get_eval_log()
        assert len(log_entries) == 2

    def test_clear_log(self):
        ev = FeatureFlagEvaluator()
        ev.register(FeatureFlag(key="f", description="F"))
        ev.evaluate("f", EvalContext())
        ev.clear_eval_log()
        assert len(ev.get_eval_log()) == 0
