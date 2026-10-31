from app.services.app_marketplace_app_throttle_manager import calculate_throttle, get_throttle_config

def test_normal():
    r = calculate_throttle(current_rps=50, max_rps=100, cpu_usage=40, memory_usage=50)
    assert not r["throttled"]
    assert r["recommendation"] == "normal"

def test_throttled():
    r = calculate_throttle(current_rps=150, max_rps=100, cpu_usage=85, memory_usage=60)
    assert r["throttled"]
    assert r["delay_ms"] > 0

def test_shed_load():
    r = calculate_throttle(current_rps=200, max_rps=100, cpu_usage=95, memory_usage=92)
    assert r["recommendation"] == "shed_load"

def test_config():
    r = get_throttle_config(tier="premium")
    assert r["max_rps"] == 1000
