from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_spend_v9 import fleet_cloud_spend_v9
def test_cs2_v9():
    r = fleet_cloud_spend_v9([{"daily_spend": 1000, "monthly_forecast": 30000, "budget": 50000}])
    assert r["daily_spend"] == 1000
    assert r["healthy"]
