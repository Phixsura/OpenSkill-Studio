from app.services.app_marketplace_app_app_app_app_app_app_app_analytics_dash import build_analytics

def test_analytics():
    r = build_analytics({"active_apps": 500, "total_requests": 50_000_000,
                           "avg_latency_ms": 85, "error_rate_pct": 0.5,
                           "daily_active_users": 12000, "monthly_revenue": 75000})
    assert r["health"] == "excellent"
    assert r["display_revenue"] == "$75,000"
    assert r["display_requests"] == "50.0M"
    assert r["active_apps"] == 500
