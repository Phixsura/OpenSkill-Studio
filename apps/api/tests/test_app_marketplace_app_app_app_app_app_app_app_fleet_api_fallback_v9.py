from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_fallback_v9 import fleet_api_fallback_v9
def test_afb_v9():
    r = fleet_api_fallback_v9([{"configured": True, "triggered_today": 5, "cached_responses": 50}])
    assert r["configured"] == 1
    assert r["healthy"]
