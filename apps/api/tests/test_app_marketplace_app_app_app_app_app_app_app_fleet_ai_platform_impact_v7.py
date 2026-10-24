from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_impact_v7 import fleet_ai_platform_impact_v7
def test_piv7():
    r = fleet_ai_platform_impact_v7([{"active": True, "revenue_usd": 1000000000, "savings_usd": 200000000, "prod_pct": 40, "customers_impacted": 10000000}])
    assert r["revenue"] == 1000000000
    assert r["impactful"]
