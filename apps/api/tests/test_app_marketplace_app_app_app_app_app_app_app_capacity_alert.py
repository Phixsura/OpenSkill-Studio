from app.services.app_marketplace_app_app_app_app_app_app_app_capacity_alert import check_capacity_alerts

def test_alerts():
    r = check_capacity_alerts([
        {"name": "api", "cpu_pct": 95, "memory_pct": 60, "conn_pct": 40},
        {"name": "db", "cpu_pct": 30, "memory_pct": 85, "conn_pct": 50},
        {"name": "cache", "cpu_pct": 20, "memory_pct": 30, "conn_pct": 20},
    ])
    assert r["total_alerts"] == 2
    assert r["critical"] == 1
    assert r["alerts"][0]["service"] == "api"
    assert r["alerts"][0]["bottleneck"] == "cpu"

def test_no_alerts():
    r = check_capacity_alerts([{"name": "api", "cpu_pct": 30, "memory_pct": 40, "conn_pct": 20}])
    assert r["total_alerts"] == 0
