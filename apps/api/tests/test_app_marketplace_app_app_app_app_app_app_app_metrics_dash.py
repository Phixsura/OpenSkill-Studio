from app.services.app_marketplace_app_app_app_app_app_app_app_metrics_dash import executive_dashboard, trend_analysis

def test_green():
    r = executive_dashboard({"uptime_pct": 99.99, "error_rate_pct": 0.05,
                             "p99_ms": 80, "daily_active_users": 5000})
    assert r["health"] == "green"
    assert r["sla_met"]

def test_red():
    r = executive_dashboard({"uptime_pct": 98.5, "error_rate_pct": 5.0})
    assert r["health"] == "red"

def test_trends():
    r = trend_analysis(
        {"users": 1000, "requests": 50000},
        {"users": 800, "requests": 45000})
    assert r["users"]["direction"] == "up"
    assert r["users"]["pct_change"] == 25.0
