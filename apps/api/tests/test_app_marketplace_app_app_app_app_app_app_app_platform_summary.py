from app.services.app_marketplace_app_app_app_app_app_app_app_platform_summary import generate_summary, compare_periods

def test_summary():
    r = generate_summary({"apps": 500, "users": 10000, "monthly_revenue": 50000,
                            "uptime_pct": 99.95, "growth_pct": 15, "new_apps": 25})
    assert r["health"] == "excellent"
    assert len(r["highlights"]) >= 2
    assert r["display_revenue"] == "$50,000"

def test_compare():
    c = {"apps": 500, "users": 10000, "monthly_revenue": 50000}
    p = {"apps": 400, "users": 8000, "monthly_revenue": 40000}
    r = compare_periods(c, p)
    assert r["improving"]
    assert r["deltas"]["apps"]["pct_change"] == 25.0
