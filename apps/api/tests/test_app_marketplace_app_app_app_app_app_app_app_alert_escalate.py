from app.services.app_marketplace_app_app_app_app_app_app_app_alert_escalate import (
    create_policy, escalate, simulate_escalation,
)

def test_escalate():
    p = create_policy("critical", [
        {"contacts": ["oncall"], "channel": "pager", "wait_min": 5},
        {"contacts": ["manager"], "channel": "phone", "wait_min": 15},
        {"contacts": ["director"], "channel": "phone", "wait_min": 30},
    ])
    r = escalate(p, 0)
    assert r["escalated"]
    assert r["contacts"] == ["oncall"]
    r2 = escalate(p, 2)
    assert r2["escalated"]
    r3 = escalate(p, 3)
    assert not r3["escalated"]

def test_simulate():
    p = create_policy("test", [
        {"contacts": ["a"], "wait_min": 5},
        {"contacts": ["b"], "wait_min": 10},
    ])
    t = simulate_escalation(p)
    assert t[0]["at_min"] == 0
    assert t[1]["at_min"] == 5
