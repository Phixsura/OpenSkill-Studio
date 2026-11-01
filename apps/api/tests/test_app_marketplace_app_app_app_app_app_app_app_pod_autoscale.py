from app.services.app_marketplace_app_app_app_app_app_app_app_pod_autoscale import calculate_desired_pods, scaling_history

def test_scale_up():
    r = calculate_desired_pods(3, current_metric=90, target_metric=50)
    assert r["action"] == "scale_up"
    assert r["clamped"] >= 5

def test_scale_down():
    r = calculate_desired_pods(10, current_metric=20, target_metric=50)
    assert r["action"] == "scale_down"

def test_clamped():
    r = calculate_desired_pods(5, current_metric=500, target_metric=50, max_pods=10)
    assert r["clamped"] == 10

def test_history():
    r = scaling_history([
        {"action": "scale_up"}, {"action": "scale_up"},
        {"action": "no_change"}, {"action": "scale_down"},
    ])
    assert r["scale_ups"] == 2
    assert r["scale_downs"] == 1
