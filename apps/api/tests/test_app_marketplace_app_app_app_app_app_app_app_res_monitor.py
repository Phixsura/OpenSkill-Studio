from app.services.app_marketplace_app_app_app_app_app_app_app_res_monitor import monitor_resources, resource_trend

def test_monitor():
    r = monitor_resources([
        {"name": "cpu", "type": "compute", "usage_pct": 45},
        {"name": "memory", "type": "compute", "usage_pct": 75},
        {"name": "disk", "type": "storage", "usage_pct": 95},
    ])
    assert r["healthy"] == 1
    assert r["warning_count"] == 1
    assert r["critical_count"] == 1
    assert r["status"] == "critical"

def test_trend():
    r = resource_trend([40, 45, 50, 60, 70, 80])
    assert r["trend"] == "increasing"
