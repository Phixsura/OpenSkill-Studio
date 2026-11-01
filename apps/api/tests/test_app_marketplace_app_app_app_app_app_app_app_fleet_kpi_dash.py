from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kpi_dash import fleet_kpi_dashboard
def test_kpi():
    r = fleet_kpi_dashboard({"uptime_pct": 99.95, "user_growth_pct": 15, "revenue_growth_pct": 25})
    assert r["healthy"]
    assert r["revenue_growth_pct"] == 25
