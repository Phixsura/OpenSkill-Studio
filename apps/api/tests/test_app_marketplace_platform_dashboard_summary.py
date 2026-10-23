from app.services.app_marketplace_platform_dashboard_summary import build_platform_summary

def test_summary():
    stats = {"total_apps": 500, "total_developers": 200, "total_users": 50000,
             "total_installs": 250000, "mrr": 85000, "revenue_growth_pct": 15.5,
             "uptime_pct": 99.95, "avg_latency_ms": 42, "error_rate": 0.02,
             "active_incidents": 0, "dau": 5000, "wau": 15000, "mau": 35000,
             "retention_30d": 72.5}
    r = build_platform_summary(stats=stats)
    assert r["status"] == "operational"
    assert r["revenue"]["arr"] == 1020000
    assert r["health"]["uptime_pct"] == 99.95
    assert r["engagement"]["mau"] == 35000

def test_degraded():
    r = build_platform_summary(stats={"active_incidents": 2})
    assert r["status"] == "degraded"
