from app.services.app_marketplace_app_app_usage_limit_alert import check_usage_limits

def test_alerts():
    limits = [
        {"name": "API Calls", "used": 9500, "limit": 10000, "unit": "calls"},
        {"name": "Storage", "used": 3, "limit": 10, "unit": "GB"},
        {"name": "Bandwidth", "used": 110, "limit": 100, "unit": "GB"},
    ]
    r = check_usage_limits(limits=limits)
    assert r["total_alerts"] == 2  # API at 95%, Bandwidth at 110%
    assert r["has_critical"]  # Bandwidth over 100%
    assert not r["all_ok"]

def test_all_ok():
    r = check_usage_limits(limits=[{"name": "X", "used": 10, "limit": 100}])
    assert r["all_ok"]
