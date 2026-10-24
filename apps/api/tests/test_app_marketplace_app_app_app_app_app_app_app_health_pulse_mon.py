from app.services.app_marketplace_app_app_app_app_app_app_app_health_pulse_mon import collect_pulse, pulse_history

def test_pulse():
    r = collect_pulse([
        {"name": "api", "status": "healthy", "latency_ms": 50, "threshold_ms": 200},
        {"name": "db", "status": "healthy", "latency_ms": 10},
        {"name": "cache", "status": "unhealthy", "latency_ms": 5000},
    ])
    assert r["healthy"] == 2
    assert r["health_pct"] == 67
    assert not r["all_healthy"]

def test_history():
    r = pulse_history([{"health_pct": 80}, {"health_pct": 90}])
    assert r["improving"]
