from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_impact_v8 import fleet_ai_impact_v8
def test_iv8():
    r = fleet_ai_impact_v8([{"active": True, "revenue_usd": 10000000000, "savings_usd": 2000000000, "prod_pct": 50}])
    assert r["revenue"] == 10000000000
    assert r["impactful"]
