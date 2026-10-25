from app.services.app_marketplace_extension_policy_engine import (
    PolicyEngine, PolicyRule, PolicyAction,
)


def test_allow_by_default():
    pe = PolicyEngine()
    action, reasons = pe.decide({"rating": 4.5})
    assert action == PolicyAction.ALLOW


def test_deny_low_rating():
    pe = PolicyEngine()
    pe.add_rule(PolicyRule("r1", "Low Rating", "rating.lt.2.0", PolicyAction.DENY,
                            "Rating below minimum threshold"))
    action, reasons = pe.decide({"rating": 1.5})
    assert action == PolicyAction.DENY
    assert "minimum threshold" in reasons[0]


def test_require_review():
    pe = PolicyEngine()
    pe.add_rule(PolicyRule("r2", "New Developer", "extension_count.lt.3",
                            PolicyAction.REQUIRE_REVIEW, "New developer requires review"))
    action, _ = pe.decide({"extension_count": 1})
    assert action == PolicyAction.REQUIRE_REVIEW


def test_warn_on_large_package():
    pe = PolicyEngine()
    pe.add_rule(PolicyRule("r3", "Large Package", "size_mb.gt.25",
                            PolicyAction.WARN, "Package is unusually large"))
    evals = pe.evaluate({"size_mb": 30})
    assert evals[0].matched is True
    assert evals[0].action == PolicyAction.WARN


def test_priority_ordering():
    pe = PolicyEngine()
    pe.add_rule(PolicyRule("low", "Low Priority", "score.lt.50", PolicyAction.WARN, "Low", priority=1))
    pe.add_rule(PolicyRule("high", "High Priority", "score.lt.50", PolicyAction.DENY, "Blocked", priority=10))
    action, _ = pe.decide({"score": 30})
    assert action == PolicyAction.DENY  # higher priority wins


def test_multiple_conditions():
    pe = PolicyEngine()
    pe.add_rule(PolicyRule("r4", "Banned Category", "category.eq.gambling", PolicyAction.DENY))
    pe.add_rule(PolicyRule("r5", "Allowed Category", "category.eq.tools", PolicyAction.ALLOW))
    action, _ = pe.decide({"category": "gambling"})
    assert action == PolicyAction.DENY
    action2, _ = pe.decide({"category": "tools"})
    assert action2 == PolicyAction.ALLOW


def test_in_operator():
    pe = PolicyEngine()
    pe.add_rule(PolicyRule("r6", "Region Check", "region.in.us,eu,jp", PolicyAction.ALLOW))
    evals = pe.evaluate({"region": "us"})
    assert evals[0].matched is True


def test_remove_rule():
    pe = PolicyEngine()
    pe.add_rule(PolicyRule("r7", "Temp", "x.eq.1", PolicyAction.DENY))
    assert pe.remove_rule("r7") is True
    assert len(pe.list_rules()) == 0
