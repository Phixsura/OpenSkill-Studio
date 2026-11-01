from app.services.app_marketplace_extension_flag_evaluator import (
    FlagEvaluatorService, TargetingRule, Condition
)


def test_default_when_disabled():
    svc = FlagEvaluatorService()
    config = svc.register("feature-x", default="off")
    config.enabled = False
    assert svc.evaluate("feature-x", {"user_id": "u1"}) == "off"


def test_default_when_no_rules_match():
    svc = FlagEvaluatorService()
    svc.register("feature-x", default="control")
    assert svc.evaluate("feature-x", {"user_id": "u1"}) == "control"


def test_eq_condition():
    svc = FlagEvaluatorService()
    svc.register("beta", default="off", rules=[
        TargetingRule("beta-users", [Condition("plan", "eq", "enterprise")], "on"),
    ])
    assert svc.evaluate("beta", {"plan": "enterprise"}) == "on"
    assert svc.evaluate("beta", {"plan": "free"}) == "off"


def test_in_condition():
    svc = FlagEvaluatorService()
    svc.register("vip", default="off", rules=[
        TargetingRule("vip-list", [Condition("user_id", "in", ["u1", "u2", "u3"])], "on"),
    ])
    assert svc.evaluate("vip", {"user_id": "u2"}) == "on"
    assert svc.evaluate("vip", {"user_id": "u99"}) == "off"


def test_multiple_conditions_and():
    svc = FlagEvaluatorService()
    svc.register("premium-feature", default="off", rules=[
        TargetingRule("premium", [
            Condition("plan", "eq", "pro"),
            Condition("country", "in", ["US", "UK"]),
        ], "on"),
    ])
    assert svc.evaluate("premium-feature", {"plan": "pro", "country": "US"}) == "on"
    assert svc.evaluate("premium-feature", {"plan": "pro", "country": "JP"}) == "off"
    assert svc.evaluate("premium-feature", {"plan": "free", "country": "US"}) == "off"


def test_rule_precedence():
    svc = FlagEvaluatorService()
    svc.register("ui-variant", default="A", rules=[
        TargetingRule("staff", [Condition("role", "eq", "staff")], "C"),
        TargetingRule("beta", [Condition("plan", "eq", "pro")], "B"),
    ])
    # Staff rule comes first, wins even if pro
    assert svc.evaluate("ui-variant", {"role": "staff", "plan": "pro"}) == "C"
    assert svc.evaluate("ui-variant", {"role": "user", "plan": "pro"}) == "B"
    assert svc.evaluate("ui-variant", {"role": "user", "plan": "free"}) == "A"


def test_contains_operator():
    svc = FlagEvaluatorService()
    svc.register("email-flag", default="off", rules=[
        TargetingRule("internal", [Condition("email", "contains", "@company.com")], "on"),
    ])
    assert svc.evaluate("email-flag", {"email": "alice@company.com"}) == "on"
    assert svc.evaluate("email-flag", {"email": "bob@gmail.com"}) == "off"


def test_gt_lt_operators():
    svc = FlagEvaluatorService()
    svc.register("high-value", default="standard", rules=[
        TargetingRule("whale", [Condition("spend", "gt", 10000)], "premium"),
        TargetingRule("active", [Condition("sessions", "gt", 50)], "engaged"),
    ])
    assert svc.evaluate("high-value", {"spend": 15000, "sessions": 10}) == "premium"
    assert svc.evaluate("high-value", {"spend": 500, "sessions": 100}) == "engaged"


def test_regex_operator():
    svc = FlagEvaluatorService()
    svc.register("bot-detect", default="human", rules=[
        TargetingRule("bots", [Condition("user_agent", "regex", r"bot|crawler|spider")], "bot"),
    ])
    assert svc.evaluate("bot-detect", {"user_agent": "Googlebot/2.1"}) == "bot"
    assert svc.evaluate("bot-detect", {"user_agent": "Mozilla/5.0"}) == "human"


def test_rollout_percentage():
    svc = FlagEvaluatorService()
    svc.register("gradual", default="off", rules=[
        TargetingRule("50pct", [], "on", rollout_pct=50),
    ])
    # Deterministic: count how many users out of 100 get "on"
    on_count = sum(1 for i in range(100)
                   if svc.evaluate("gradual", {"user_id": f"user-{i}"}) == "on")
    assert 30 < on_count < 70  # ~50% with some variance


def test_evaluate_all():
    svc = FlagEvaluatorService()
    svc.register("a", default="off")
    svc.register("b", default="on")
    result = svc.evaluate_all({"user_id": "u1"})
    assert result == {"a": "off", "b": "on"}


def test_missing_attribute():
    svc = FlagEvaluatorService()
    svc.register("test", default="off", rules=[
        TargetingRule("check", [Condition("missing_attr", "eq", "value")], "on"),
    ])
    assert svc.evaluate("test", {}) == "off"
