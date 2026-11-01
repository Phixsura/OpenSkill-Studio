from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_growth import fleet_ai_platform_growth
def test_pg():
    r = fleet_ai_platform_growth([{"active": True, "mau": 1000000, "mrr_usd": 5000000, "growth_pct": 30, "churn_pct": 2}])
    assert r["mau"] == 1000000
    assert r["scaling"]
