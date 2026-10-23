from app.services.app_marketplace_app_app_stat_counter import build_stat_counters

def test_counters():
    metrics = {"total_apps": 500, "total_users": 50000, "total_revenue": 85000, "uptime": 99.99}
    r = build_stat_counters(metrics=metrics)
    assert r["total"] == 4
    apps = next(c for c in r["counters"] if c["key"] == "total_apps")
    assert apps["label"] == "Total Apps"
    assert apps["icon"] == "📦"
    assert apps["animate"]

def test_unknown_metric():
    r = build_stat_counters(metrics={"custom_metric": 42})
    assert r["counters"][0]["label"] == "Custom Metric"
