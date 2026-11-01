from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_playground_v9 import fleet_api_playground_v9
def test_apg_v9():
    r = fleet_api_playground_v9([{"active": True, "requests_today": 5000, "user": "dev1"}])
    assert r["unique_users"] == 1
    assert r["healthy"]
