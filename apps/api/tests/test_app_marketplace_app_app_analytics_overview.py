from app.services.app_marketplace_app_app_analytics_overview import build_analytics_overview

def test_overview():
    metrics = {"installs": 1000, "uninstalls": 100, "retention_30d": 72.5,
               "revenue": 5000, "mrr": 1500, "paying_users": 50,
               "api_calls": 100000, "errors": 50, "avg_latency_ms": 45,
               "dau": 500, "wau": 2000, "mau": 5000}
    r = build_analytics_overview(app_id="a1", metrics=metrics)
    assert r["acquisition"]["net"] == 900
    assert r["engagement"]["retention_30d"] == 72.5
    assert r["performance"]["error_rate"] == 0.05
    assert r["revenue"]["arpu"] == 100.0
