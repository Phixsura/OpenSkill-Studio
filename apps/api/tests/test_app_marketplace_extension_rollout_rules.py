from app.services.app_marketplace_extension_rollout_rules import (
    RolloutRulesEngine, RolloutRule,
)


def test_simple_enabled():
    engine = RolloutRulesEngine()
    engine.add_rule(RolloutRule("r1", "dark_mode"))
    result = engine.evaluate("dark_mode", "org-1")
    assert result["enabled"] is True


def test_no_rules():
    engine = RolloutRulesEngine()
    result = engine.evaluate("unknown_feature", "org-1")
    assert result["enabled"] is False
    assert result["reason"] == "no_rules"


def test_allowlist():
    engine = RolloutRulesEngine()
    engine.add_rule(RolloutRule("r2", "beta", percentage=0, org_allowlist=["vip-org"]))
    assert engine.evaluate("beta", "vip-org")["enabled"] is True
    assert engine.evaluate("beta", "normal-org")["enabled"] is False


def test_blocklist():
    engine = RolloutRulesEngine()
    engine.add_rule(RolloutRule("r3", "feature_x", org_blocklist=["banned-org"]))
    assert engine.evaluate("feature_x", "banned-org")["enabled"] is False
    assert engine.evaluate("feature_x", "ok-org")["enabled"] is True


def test_percentage_rollout():
    engine = RolloutRulesEngine()
    engine.add_rule(RolloutRule("r4", "new_ui", percentage=50))
    results = {engine.evaluate("new_ui", f"org-{i}")["enabled"] for i in range(100)}
    assert True in results and False in results


def test_plan_gating():
    engine = RolloutRulesEngine()
    engine.add_rule(RolloutRule("r5", "premium_feature", min_plan="pro"))
    assert engine.evaluate("premium_feature", "org-1", plan="pro")["enabled"] is True
    assert engine.evaluate("premium_feature", "org-1", plan="free")["enabled"] is False


def test_date_range():
    engine = RolloutRulesEngine()
    engine.add_rule(RolloutRule("r6", "holiday_promo", start_date="2026-12-01", end_date="2026-12-31"))
    assert engine.evaluate("holiday_promo", "org-1", now="2026-12-15")["enabled"] is True
    assert engine.evaluate("holiday_promo", "org-1", now="2026-11-15")["enabled"] is False


def test_bulk_evaluate():
    engine = RolloutRulesEngine()
    engine.add_rule(RolloutRule("r7", "feat_a"))
    engine.add_rule(RolloutRule("r8", "feat_b", enabled=False))
    results = engine.bulk_evaluate(["feat_a", "feat_b", "feat_c"], "org-1")
    assert results["feat_a"] is True
    assert results["feat_b"] is False
    assert results["feat_c"] is False
