from app.services.app_marketplace_app_app_app_app_app_app_app_alert_suppress import (
    create_rule, should_suppress, suppression_stats, clear_rules,
)

def test_suppress():
    clear_rules()
    r = create_rule("deploy-silence", "deploy.*", 30, "Deploying")
    assert r["active"]
    s = should_suppress("deploy-failed")
    assert s["suppress"]
    assert s["rule"] == "deploy-silence"
    s2 = should_suppress("cpu-high")
    assert not s2["suppress"]
    clear_rules()

def test_stats():
    clear_rules()
    create_rule("a", "test.*", 60, "Testing")
    should_suppress("test-alert")
    should_suppress("test-warn")
    s = suppression_stats()
    assert s["total_suppressed"] == 2
    clear_rules()
