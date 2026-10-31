from app.services.app_marketplace_app_app_app_app_app_app_app_autoscaler import calculate_replicas, cooldown_check, fleet_status

def test_scale_up():
    r = calculate_replicas(current=3, cpu_pct=90, target_cpu=70)
    assert r["action"] == "scale_up"
    assert r["clamped"] == 4

def test_scale_down():
    r = calculate_replicas(current=5, cpu_pct=30, target_cpu=70)
    assert r["action"] == "scale_down"

def test_clamped():
    r = calculate_replicas(current=1, cpu_pct=200, target_cpu=70, max_replicas=3)
    assert r["clamped"] == 3

def test_cooldown():
    r = cooldown_check(last_scale_at=100, now=401, cooldown_seconds=300)
    assert r["can_scale"]

def test_fleet():
    r = fleet_status([
        {"replicas": 3, "cpu_pct": 80, "action": "scale_up"},
        {"replicas": 2, "cpu_pct": 40, "action": "no_change"},
    ])
    assert r["total_replicas"] == 5
    assert r["currently_scaling"] == 1
