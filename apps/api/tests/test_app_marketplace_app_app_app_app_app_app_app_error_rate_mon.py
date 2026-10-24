from app.services.app_marketplace_app_app_app_app_app_app_app_error_rate_mon import monitor_error_rate

def test_monitor():
    r = monitor_error_rate([
        {"name": "api", "requests": 10000, "errors": 5, "threshold_pct": 1.0},
        {"name": "worker", "requests": 1000, "errors": 50, "threshold_pct": 1.0},
    ])
    assert r["alerting"] == 1
    assert "worker" in r["alert_services"]
    assert not r["all_ok"]
