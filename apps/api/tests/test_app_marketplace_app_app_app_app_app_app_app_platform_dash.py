from app.services.app_marketplace_app_app_app_app_app_app_app_platform_dash import build_dashboard, trend_indicator

def test_dashboard():
    r = build_dashboard({
        "apps": {"total": 500, "active": 450, "healthy_pct": 95},
        "infra": {"services": 50, "uptime_pct": 99.9, "incidents": 2},
        "users": {"total": 10000, "active_today": 3000, "satisfaction_pct": 88},
    })
    assert r["status"] == "healthy"
    assert r["health_score"] > 90
    assert r["apps"]["total"] == 500

def test_trend():
    r = trend_indicator(99.5, 98.0)
    assert r["trend"] == "up"
    assert r["delta"] == 1.5
