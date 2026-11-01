from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_consumer_v9 import fleet_api_consumer_v9
def test_acons_v9():
    r = fleet_api_consumer_v9([{"active": True, "calls_today": 50000, "plan": "enterprise"}])
    assert r["active"] == 1
    assert r["healthy"]
