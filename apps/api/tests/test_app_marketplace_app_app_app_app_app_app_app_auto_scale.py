from app.services.app_marketplace_app_app_app_app_app_app_app_auto_scale import create_scaling_policy, evaluate_scaling_decision

def test_scale_up():
    p = create_scaling_policy("cpu", "cpu_pct", 70, min_replicas=1, max_replicas=10)
    r = evaluate_scaling_decision(p, 3, 90)
    assert r["action"] == "scale_up"
    assert r["desired"] > 3

def test_scale_down():
    p = create_scaling_policy("cpu", "cpu_pct", 70, min_replicas=1, max_replicas=10)
    r = evaluate_scaling_decision(p, 5, 30)
    assert r["action"] == "scale_down"

def test_none():
    p = create_scaling_policy("cpu", "cpu_pct", 70)
    r = evaluate_scaling_decision(p, 3, 70)
    assert r["action"] == "none"
