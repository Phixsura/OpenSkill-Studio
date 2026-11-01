from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_product_health_v9 import fleet_api_product_health_v9
def test_aph2_v9():
    r = fleet_api_product_health_v9([{"healthy": True, "monthly_revenue": 50000, "adoption_pct": 85}])
    assert r["all_healthy"]
