from app.services.app_marketplace_extension_rule_engine import (
    RuleEngineService, Condition
)


def test_simple_rule():
    engine = RuleEngineService()
    engine.add_rule("greet", [Condition("name", "exists")],
                    [{"type": "assert", "key": "greeting", "value": "hello"}])
    engine.assert_fact("name", "Alice")
    engine.evaluate()
    assert engine.get_facts()["greeting"] == "hello"


def test_condition_operators():
    engine = RuleEngineService()
    engine.add_rule("discount", [
        Condition("age", "gte", 65),
        Condition("member", "eq", True),
    ], [{"type": "assert", "key": "discount", "value": 20}])
    engine.assert_fact("age", 70)
    engine.assert_fact("member", True)
    engine.evaluate()
    assert engine.get_facts()["discount"] == 20


def test_condition_not_met():
    engine = RuleEngineService()
    engine.add_rule("vip", [Condition("spend", "gt", 10000)],
                    [{"type": "assert", "key": "vip", "value": True}])
    engine.assert_fact("spend", 500)
    engine.evaluate()
    assert "vip" not in engine.get_facts()


def test_rule_chaining():
    engine = RuleEngineService()
    # Rule 1: temperature > 100 → assert overheating
    engine.add_rule("detect_heat", [Condition("temperature", "gt", 100)],
                    [{"type": "assert", "key": "overheating", "value": True}])
    # Rule 2: overheating → assert alarm
    engine.add_rule("alarm", [Condition("overheating", "eq", True)],
                    [{"type": "assert", "key": "alarm", "value": "CRITICAL"}])
    engine.assert_fact("temperature", 150)
    log = engine.evaluate()
    facts = engine.get_facts()
    assert facts["overheating"] is True
    assert facts["alarm"] == "CRITICAL"
    assert len(log) >= 2  # both rules fired


def test_priority():
    engine = RuleEngineService()
    engine.add_rule("low", [Condition("x", "exists")],
                    [{"type": "assert", "key": "fired_by", "value": "low"}], priority=1)
    engine.add_rule("high", [Condition("x", "exists")],
                    [{"type": "assert", "key": "fired_by", "value": "high"}], priority=10)
    engine.assert_fact("x", True)
    engine.evaluate()
    assert engine.get_facts()["fired_by"] == "high"  # high priority fires first


def test_retract_action():
    engine = RuleEngineService()
    engine.add_rule("cleanup", [Condition("temp_data", "exists")],
                    [{"type": "retract", "key": "temp_data"},
                     {"type": "assert", "key": "cleaned", "value": True}])
    engine.assert_fact("temp_data", "some value")
    engine.evaluate()
    facts = engine.get_facts()
    assert "temp_data" not in facts
    assert facts["cleaned"] is True


def test_not_exists():
    engine = RuleEngineService()
    engine.add_rule("default", [Condition("config", "not_exists")],
                    [{"type": "assert", "key": "config", "value": "default"}])
    engine.evaluate()
    assert engine.get_facts()["config"] == "default"


def test_no_infinite_loop():
    engine = RuleEngineService()
    # Rule that constantly asserts → would loop without duplicate detection
    engine.add_rule("loop", [Condition("x", "eq", 1)],
                    [{"type": "set", "key": "x", "value": 1}])
    engine.assert_fact("x", 1)
    log = engine.evaluate()
    assert len(log) < 10  # should stop quickly


def test_matching_rules():
    engine = RuleEngineService()
    engine.add_rule("a", [Condition("x", "eq", 1)], [])
    engine.add_rule("b", [Condition("x", "eq", 2)], [])
    engine.assert_fact("x", 1)
    assert engine.get_matching_rules() == ["a"]


def test_disabled_rule():
    engine = RuleEngineService()
    rule = engine.add_rule("test", [Condition("x", "exists")],
                           [{"type": "assert", "key": "y", "value": 1}])
    rule.enabled = False
    engine.assert_fact("x", True)
    engine.evaluate()
    assert "y" not in engine.get_facts()
