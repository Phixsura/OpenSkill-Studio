from app.services.app_marketplace_app_metrics_collector import collect_metrics, compute_trend, build_dashboard_metrics

def test_collect():
    dp = [{"metric": "latency", "value": 100}, {"metric": "latency", "value": 200}, {"metric": "errors", "value": 1}]
    r = collect_metrics(data_points=dp)
    assert r["metrics"]["latency"]["avg"] == 150
    assert r["total_points"] == 3

def test_trend_up():
    t = compute_trend(current=150, previous=100)
    assert t["direction"] == "up"
    assert t["change_pct"] == 50.0

def test_trend_down():
    t = compute_trend(current=50, previous=100)
    assert t["direction"] == "down"

def test_trend_zero():
    t = compute_trend(current=10, previous=0)
    assert t["direction"] == "up"

def test_dashboard_healthy():
    m = build_dashboard_metrics(installs=100, uninstalls=10, api_calls=10000, errors=5, avg_response_ms=120)
    assert m["health"] == "healthy"
    assert m["net_installs"] == 90

def test_dashboard_critical():
    m = build_dashboard_metrics(installs=10, uninstalls=5, api_calls=100, errors=10, avg_response_ms=500)
    assert m["health"] == "critical"
