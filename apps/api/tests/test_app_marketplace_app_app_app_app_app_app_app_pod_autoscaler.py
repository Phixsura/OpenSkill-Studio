from app.services.app_marketplace_app_app_app_app_app_app_app_pod_autoscaler import compute_replicas

def test_scale_up():
    r = compute_replicas(current_replicas=3, current_cpu_pct=90, target_cpu_pct=70)
    assert r["action"] == "scale_up"
    assert r["target_replicas"] > 3

def test_scale_down():
    r = compute_replicas(current_replicas=10, current_cpu_pct=30, target_cpu_pct=70, min_replicas=2)
    assert r["action"] == "scale_down"
    assert r["target_replicas"] < 10
    assert r["target_replicas"] >= 2

def test_cooldown():
    r = compute_replicas(current_replicas=5, current_cpu_pct=90, cooldown_remaining_sec=30)
    assert r["action"] == "cooldown"
    assert r["target_replicas"] == 5
