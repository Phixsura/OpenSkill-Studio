from app.services.app_marketplace_app_app_app_app_app_app_app_resource_scaler import (
    create_scaling_policy, evaluate_scaling, scaling_history,
)

def test_scale_up():
    p = create_scaling_policy("api", min_replicas=2, max_replicas=10, target_cpu=70)
    r = evaluate_scaling(p, current_replicas=3, current_cpu=95)
    assert r["action"] == "scale_up"
    assert r["desired"] > 3

def test_scale_down():
    p = create_scaling_policy("api", min_replicas=1, max_replicas=10, target_cpu=70)
    r = evaluate_scaling(p, current_replicas=5, current_cpu=30)
    assert r["action"] == "scale_down"
    assert r["desired"] < 5

def test_no_change():
    p = create_scaling_policy("api", target_cpu=70)
    r = evaluate_scaling(p, current_replicas=3, current_cpu=70)
    assert r["action"] == "none"

def test_history():
    events = [{"action": "scale_up"}, {"action": "none"}, {"action": "scale_down"}]
    r = scaling_history(events)
    assert r["scale_ups"] == 1
    assert not r["stable"]
