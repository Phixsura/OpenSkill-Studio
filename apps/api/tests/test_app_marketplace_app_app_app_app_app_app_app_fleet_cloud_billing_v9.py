from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_billing_v9 import fleet_cloud_billing_v9
def test_cb3_v9():
    r = fleet_cloud_billing_v9([{"monthly_spend": 50000, "credits_remaining": 10000, "forecast": 55000}])
    assert r["monthly_spend"] == 50000
    assert r["healthy"]
