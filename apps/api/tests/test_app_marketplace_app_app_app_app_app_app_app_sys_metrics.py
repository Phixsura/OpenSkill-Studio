from app.services.app_marketplace_app_app_app_app_app_app_app_sys_metrics import collect_metrics, trend_metrics

def test_healthy():
    r = collect_metrics(45, 60, 50, 100)
    assert r["status"] == "healthy"
    assert r["alert_count"] == 0

def test_critical():
    r = collect_metrics(95, 92, 90)
    assert r["status"] == "critical"
    assert r["alert_count"] == 3

def test_trend():
    history = [
        {"cpu_pct": 50, "memory_pct": 60},
        {"cpu_pct": 65, "memory_pct": 55},
    ]
    r = trend_metrics(history)
    assert r["cpu_trend"] == "up"
    assert r["mem_trend"] == "down"
    assert r["cpu_delta"] == 15
